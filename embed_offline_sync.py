import sys

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

pos_start = code.find('window.__BISTRO_OFFLINE_SYNC__=')
pos_fn_start = code.rfind('(function(){', 0, pos_start)
pos_fn_end = code.find('})();', pos_start) + 5

old_block = code[pos_fn_start:pos_fn_end]

new_block = '''(function(){
  if (typeof window === "undefined") return;

  var QUEUE_KEY = "bistro_sync_queue";
  var LEGACY_SALES_KEY = "bistro_pending_sales";
  var CATALOG_PREFIX = "bistro_local_catalog_";
  var LAST_SYNC_PREFIX = "bistro_last_sync_timestamp_";
  var isSyncing = false;
  var isOnline = typeof navigator !== "undefined" ? navigator.onLine : true;
  var backoffMs = 3000;

  var offlineManager = {
    getQueue: function() {
      try {
        var raw = localStorage.getItem(QUEUE_KEY);
        var queue = raw ? JSON.parse(raw) : [];
        if (!Array.isArray(queue)) queue = [];

        // Migrate legacy pending sales if any exist
        var legacyRaw = localStorage.getItem(LEGACY_SALES_KEY);
        if (legacyRaw) {
          try {
            var legacyList = JSON.parse(legacyRaw);
            if (Array.isArray(legacyList) && legacyList.length > 0) {
              legacyList.forEach(function(leg) {
                if (!queue.some(function(q) { return q.id === leg.id || q.payload?.sale?.id === leg.sale?.id; })) {
                  queue.push({
                    id: leg.id || (typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : "sale-" + Date.now()),
                    action: "SALE",
                    table: "sales",
                    payload: {
                      sale: leg.sale,
                      branchId: leg.branchId,
                      tenantId: leg.tenantId || "biz-main",
                      deductions: leg.stockDeductions || []
                    },
                    client_created_at: leg.createdAt || new Date().toISOString(),
                    status: "pending",
                    retry_count: leg.retryCount || 0
                  });
                }
              });
              localStorage.removeItem(LEGACY_SALES_KEY);
              localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
            }
          } catch(e) {}
        }

        return queue.sort(function(a, b) {
          return new Date(a.client_created_at).getTime() - new Date(b.client_created_at).getTime();
        });
      } catch(e) {
        return [];
      }
    },

    saveQueue: function(queue) {
      try {
        localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
      } catch(e) {}
      this.notifyStatus();
    },

    getPendingCount: function() {
      return this.getQueue().length;
    },

    // -------------------------------------------------------------
    // Enqueue Operation (Chronological FIFO)
    // -------------------------------------------------------------
    enqueue: function(action, table, payload) {
      try {
        var queue = this.getQueue();
        var id = (typeof crypto !== "undefined" && crypto.randomUUID) 
          ? crypto.randomUUID() 
          : "op-" + Date.now() + "-" + Math.random().toString(36).slice(2, 7);

        var item = {
          id: id,
          action: action,
          table: table,
          payload: payload,
          client_created_at: new Date().toISOString(),
          status: "pending",
          retry_count: 0
        };

        // Decrement local stock immediately if it is a sale to prevent overselling
        if (action === "SALE" && payload.deductions && payload.deductions.length > 0) {
          this.decrementLocalStock(payload.branchId, payload.deductions);
        }

        queue.push(item);
        this.saveQueue(queue);

        // If online, trigger background flush immediately without blocking UI
        if (isOnline && !isSyncing) {
          var self = this;
          setTimeout(function() { self.flushQueue(); }, 50);
        }

        return item;
      } catch(e) {
        console.warn("[OfflineSync] Enqueue error:", e);
        return null;
      }
    },

    enqueueSale: function(sale, branchId, tenantId, deductions) {
      return this.enqueue("SALE", "sales", {
        sale: sale,
        branchId: branchId,
        tenantId: tenantId || "biz-main",
        deductions: deductions || []
      });
    },

    // -------------------------------------------------------------
    // Immediate Local Stock Decrement
    // -------------------------------------------------------------
    decrementLocalStock: function(branchId, deductions) {
      if (!deductions || deductions.length === 0) return;
      var catKey = CATALOG_PREFIX + (branchId || "branch-1792458194300-3i4l");
      try {
        var raw = localStorage.getItem(catKey);
        var catalog = raw ? JSON.parse(raw) : [];
        if (Array.isArray(catalog) && catalog.length > 0) {
          var changed = false;
          deductions.forEach(function(ded) {
            var target = catalog.find(function(it) {
              return it.id === ded.id || it.item_id === ded.id;
            });
            if (target) {
              var curr = Number(target.current_stock ?? target.stock ?? 0);
              var next = Math.max(0, curr - Number(ded.quantity || 1));
              target.current_stock = next;
              target.stock = next;
              changed = true;
            }
          });
          if (changed) {
            localStorage.setItem(catKey, JSON.stringify(catalog));
            window.dispatchEvent(new CustomEvent("bistro_catalog_updated", {
              detail: { branchId: branchId, count: catalog.length }
            }));
          }
        }
      } catch(e) {}
    },

    // -------------------------------------------------------------
    // Network Connectivity & Health Check
    // -------------------------------------------------------------
    checkRealConnection: async function() {
      if (typeof navigator !== "undefined" && !navigator.onLine) {
        isOnline = false;
        this.notifyStatus();
        return false;
      }
      try {
        var client = window.__BISTRO_SUPABASE_CLIENT__;
        var url = (client && client.supabaseUrl) ? client.supabaseUrl : "https://yohpvligtqppphjrmxeq.supabase.co";
        var key = (client && client.supabaseKey) ? client.supabaseKey : "sb_publishable_couMOQUQA8PDOqHvY1XvnA_jG_3_E8W";
        
        var controller = new AbortController();
        var timeoutId = setTimeout(function() { controller.abort(); }, 4000);
        var res = await fetch(url + "/rest/v1/", {
          method: "HEAD",
          headers: { apikey: key },
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        isOnline = res.ok || res.status < 500;
      } catch(e) {
        isOnline = false;
      }
      this.notifyStatus();
      return isOnline;
    },

    // -------------------------------------------------------------
    // Chronological Sequential Flush (Strict FIFO)
    // -------------------------------------------------------------
    flushQueue: async function() {
      if (isSyncing) return { processed: 0, failed: 0 };
      
      var online = await this.checkRealConnection();
      if (!online) {
        return { processed: 0, failed: 0 };
      }

      var queue = this.getQueue();
      if (queue.length === 0) {
        this.notifyStatus();
        return { processed: 0, failed: 0 };
      }

      var client = window.__BISTRO_SUPABASE_CLIENT__;
      if (!client) {
        return { processed: 0, failed: 0 };
      }

      isSyncing = true;
      this.notifyStatus("Sincronizando operaciones...");
      var processed = 0;
      var failed = 0;

      try {
        for (var i = 0; i < queue.length; i++) {
          var item = queue[i];
          item.status = "syncing";
          this.saveQueue(queue);

          var success = false;
          try {
            if (item.action === "SALE") {
              var s = item.payload.sale;
              var salePayload = {
                id: s.id,
                tenant_id: item.payload.tenantId || s.tenant_id || "biz-main",
                branch_id: item.payload.branchId || s.branchId || s.branch_id,
                sale_number: s.saleNumber || s.sale_number,
                date: s.date,
                time: s.time,
                subtotal: s.subtotal || s.totalAmount || 0,
                tax_amount: s.taxAmount || 0,
                tip_amount: s.tipAmount || 0,
                total_amount: s.totalAmount || s.amountCUP || 0,
                payment_method: s.paymentMethod || "Efectivo",
                status: s.status || "completed",
                data: s
              };
              var saleRes = await client.from("sales").upsert(salePayload, { onConflict: "id" });
              if (saleRes.error) throw saleRes.error;

              // Deduct stock in remote branch_inventory
              var deds = item.payload.deductions || [];
              for (var d = 0; d < deds.length; d++) {
                try {
                  var ded = deds[d];
                  var bRes = await client.from("branch_inventory")
                    .select("id, current_stock")
                    .eq("branch_id", salePayload.branch_id)
                    .eq("item_id", ded.id)
                    .order("updated_at", { ascending: false })
                    .limit(1)
                    .maybeSingle();

                  if (bRes.data && bRes.data.id) {
                    var curDbStock = Number(bRes.data.current_stock || 0);
                    var newStock = ded.newBranchStock !== undefined ? ded.newBranchStock : Math.max(0, curDbStock - (ded.quantity || 1));
                    await client.from("branch_inventory").update({
                      current_stock: newStock,
                      updated_at: new Date().toISOString()
                    }).eq("id", bRes.data.id);
                  }
                } catch(stkErr) {}
              }
              success = true;
            } else if (item.action === "SHIFT_START" || item.action === "SHIFT_END") {
              var shiftRes = await client.from("work_shifts").upsert(item.payload, { onConflict: "id" });
              if (shiftRes.error) throw shiftRes.error;
              success = true;
            } else if (item.action === "IPV_SUBMIT") {
              var ipvRes = await client.from("ipv_reports").upsert(item.payload, { onConflict: "id" });
              if (ipvRes.error) throw ipvRes.error;
              success = true;
            } else {
              success = true;
            }
          } catch(err) {
            console.error("[OfflineSync] Error procesando transaccion FIFO:", err);
            item.status = "failed";
            item.retry_count = (item.retry_count || 0) + 1;
            item.last_error = err?.message || String(err);
            failed++;
            this.saveQueue(queue);

            // Pause queue processing to preserve strict chronological ordering
            backoffMs = Math.min(backoffMs * 2, 30000);
            var self = this;
            setTimeout(function() {
              if (isOnline && !isSyncing) self.flushQueue();
            }, backoffMs);
            break;
          }

          if (success) {
            // Remove from queue
            queue = queue.filter(function(q) { return q.id !== item.id; });
            this.saveQueue(queue);
            processed++;
            backoffMs = 3000;
          }
        }

        // If queue completely flushed, perform delta sync
        if (queue.length === 0) {
          var activeBranch = localStorage.getItem("bistro_selected_branch_id") || "branch-1792458194300-3i4l";
          await this.reconcileDelta(activeBranch);
        }
      } finally {
        isSyncing = false;
        this.notifyStatus(processed > 0 ? (processed + " transacciones sincronizadas con Supabase") : undefined);
      }

      return { processed: processed, failed: failed };
    },

    // -------------------------------------------------------------
    // Delta Sync & Reconciliation
    // -------------------------------------------------------------
    reconcileDelta: async function(branchId) {
      var client = window.__BISTRO_SUPABASE_CLIENT__;
      if (!client || !isOnline) return;

      var timeKey = LAST_SYNC_PREFIX + (branchId || "branch-1792458194300-3i4l");
      var lastTime = localStorage.getItem(timeKey);

      try {
        var query = client.from("branch_inventory")
          .select("id, branch_id, item_id, current_stock, min_stock, updated_at, inventory:item_id (id, name, category, selling_price_cup, selling_price_usd, barcode, sku, unit, active, status)")
          .eq("branch_id", branchId || "branch-1792458194300-3i4l")
          .order("updated_at", { ascending: false });

        if (lastTime) {
          query = query.gt("updated_at", lastTime);
        }

        var res = await query;
        if (!res.error && Array.isArray(res.data) && res.data.length > 0) {
          var catKey = CATALOG_PREFIX + (branchId || "branch-1792458194300-3i4l");
          var raw = localStorage.getItem(catKey);
          var catalog = raw ? JSON.parse(raw) : [];
          var catMap = new Map();
          if (Array.isArray(catalog)) {
            catalog.forEach(function(it) { catMap.set(it.id || it.item_id, it); });
          }

          res.data.forEach(function(row) {
            var inv = row.inventory || {};
            var itemId = row.item_id || inv.id;
            if (!itemId) return;
            var price = Number(inv.selling_price_cup || 100);
            var stock = Number(row.current_stock || 0);

            catMap.set(itemId, {
              id: itemId,
              item_id: itemId,
              name: inv.name || ("Producto " + itemId),
              category: inv.category || "Sellados / Enlatados",
              price: price,
              selling_price_cup: price,
              selling_price_usd: Number(inv.selling_price_usd || 0),
              current_stock: stock,
              stock: stock,
              min_stock: Number(row.min_stock || 1),
              unit: inv.unit || "uds",
              sku: inv.sku || "",
              barcode: inv.barcode || "",
              productType: inv.product_type || "sealed_canned",
              active: inv.active !== false,
              branch_id: branchId,
              updated_at: row.updated_at
            });
          });

          localStorage.setItem(catKey, JSON.stringify(Array.from(catMap.values())));
          window.dispatchEvent(new CustomEvent("bistro_catalog_updated", {
            detail: { branchId: branchId, deltaCount: res.data.length }
          }));
        }

        localStorage.setItem(timeKey, new Date().toISOString());
      } catch(err) {
        console.warn("[OfflineSync] Error en reconciliacion delta:", err);
      }
    },

    // -------------------------------------------------------------
    // Status & Event Emitters
    // -------------------------------------------------------------
    getStatus: function() {
      var count = this.getPendingCount();
      var state = "online_synced";
      if (isSyncing) {
        state = "syncing";
      } else if (!isOnline || count > 0) {
        state = "offline_pending";
      }

      var activeBranch = (typeof localStorage !== "undefined" && localStorage.getItem("bistro_selected_branch_id")) || "branch-1792458194300-3i4l";
      var lastSync = typeof localStorage !== "undefined" ? localStorage.getItem(LAST_SYNC_PREFIX + activeBranch) : null;

      return {
        isOnline: isOnline,
        isSyncing: isSyncing,
        pendingCount: count,
        lastSyncTimestamp: lastSync,
        state: state
      };
    },

    notifyStatus: function(msg) {
      if (typeof window === "undefined") return;
      var status = this.getStatus();
      if (msg) status.message = msg;

      window.dispatchEvent(new CustomEvent("bistro_sync_status_changed", { detail: status }));
      window.dispatchEvent(new CustomEvent("bistro_offline_sync_updated", { detail: { count: status.pendingCount, message: msg } }));
    },

    // Backward compatibility aliases
    getPending: function() {
      return this.getQueue().map(function(q) {
        return {
          id: q.id,
          sale: q.payload?.sale || q.payload,
          branchId: q.payload?.branchId,
          tenantId: q.payload?.tenantId || "biz-main",
          stockDeductions: q.payload?.deductions || [],
          createdAt: q.client_created_at
        };
      });
    },

    remove: function(id) {
      var queue = this.getQueue().filter(function(it) {
        return it.id !== id && it.payload?.sale?.id !== id;
      });
      this.saveQueue(queue);
    },

    syncAll: function() {
      return this.flushQueue();
    }
  };

  window.__BISTRO_OFFLINE_SYNC__ = offlineManager;

  // Global event listeners
  window.addEventListener("online", function() {
    console.log("[OfflineSync] Conexión detectada. Verificando y procesando cola...");
    offlineManager.checkRealConnection().then(function(online) {
      if (online) offlineManager.flushQueue();
    });
  });

  window.addEventListener("offline", function() {
    isOnline = false;
    offlineManager.notifyStatus("Sin señal de internet");
  });

  // Periodic flush & heartbeat every 15s
  setInterval(function() {
    if (typeof navigator !== "undefined" && navigator.onLine && offlineManager.getPendingCount() > 0 && !isSyncing) {
      offlineManager.flushQueue();
    }
  }, 15000);

  // Initial check on load
  setTimeout(function() {
    offlineManager.checkRealConnection().then(function(online) {
      if (online && offlineManager.getPendingCount() > 0) {
        offlineManager.flushQueue();
      }
    });
  }, 1000);
})();'''

code = code[:pos_fn_start] + new_block + code[pos_fn_end:]

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Offline-First Sync Engine successfully embedded in bundle!")
