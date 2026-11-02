/**
 * BistroConta Offline-First Synchronization Architecture
 * 
 * Provides robust offline-first operation with chronologically ordered (FIFO)
 * bidirectional synchronization, dual-layer storage (IndexedDB + LocalStorage),
 * immediate local stock decrement to prevent overselling, and delta sync reconciliation.
 */

import { supabase, SUPABASE_URL, SUPABASE_ANON_KEY } from '../lib/supabase';

export type SyncAction = 'SALE' | 'SHIFT_START' | 'SHIFT_END' | 'IPV_SUBMIT' | 'BATCH_PRODUCTION' | 'PRODUCTION_BATCH';
export type SyncStatus = 'pending' | 'syncing' | 'failed';

export interface SyncQueueItem {
  id: string;
  action: SyncAction;
  table: string;
  payload: any;
  client_created_at: string;
  status: SyncStatus;
  retry_count: number;
  last_error?: string;
}

export interface CatalogItem {
  id: string;
  item_id?: string;
  name: string;
  category?: string;
  price: number;
  selling_price_cup?: number;
  selling_price_usd?: number;
  current_stock: number;
  stock?: number;
  min_stock?: number;
  unit?: string;
  sku?: string;
  barcode?: string;
  productType?: string;
  active?: boolean;
  branch_id?: string;
  updated_at?: string;
}

export interface SyncEngineStatus {
  isOnline: boolean;
  isSyncing: boolean;
  pendingCount: number;
  lastSyncTimestamp: string | null;
  state: 'online_synced' | 'offline_pending' | 'syncing';
  message?: string;
}

const DB_NAME = 'bistro_pos_offline_db';
const DB_VERSION = 1;
const QUEUE_STORAGE_KEY = 'bistro_sync_queue';
const CATALOG_STORAGE_PREFIX = 'bistro_local_catalog_';
const SHIFTS_STORAGE_PREFIX = 'bistro_local_shifts_';
const LAST_SYNC_PREFIX = 'bistro_last_sync_timestamp_';
const SYNC_EVENT_NAME = 'bistro_sync_status_changed';

export const DEFAULT_FALLBACK_BRANCHES = [
  {
    id: "branch-main",
    name: "Almacén Central & Matriz",
    code: "MAT",
    address: "Sede Central",
    isMainWarehouse: true,
    active: true,
    workMode: "restaurante",
    colorTag: "blue"
  },
  {
    id: "branch-1792458194300-3i4l",
    name: "Cafeteria Calle A",
    code: "CCA",
    address: "Calle A",
    isMainWarehouse: false,
    active: true,
    workMode: "cafeteria",
    colorTag: "emerald"
  }
];

export function getLocalBranches(): any[] {
  if (typeof localStorage === 'undefined') return DEFAULT_FALLBACK_BRANCHES;
  try {
    const b = localStorage.getItem('bistro_branches');
    if (b) {
      const parsed = JSON.parse(b);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
    const c = localStorage.getItem('cache_branches');
    if (c) {
      const parsed = JSON.parse(c);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
    const l = localStorage.getItem('bistro_local_branches');
    if (l) {
      const parsed = JSON.parse(l);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {
    console.warn('[LocalStore] getLocalBranches error:', e);
  }
  return DEFAULT_FALLBACK_BRANCHES;
}

export function saveLocalBranches(branches: any[]): void {
  if (typeof localStorage === 'undefined' || !Array.isArray(branches) || branches.length === 0) return;
  try {
    const serialized = JSON.stringify(branches);
    localStorage.setItem('bistro_branches', serialized);
    localStorage.setItem('cache_branches', serialized);
    localStorage.setItem('bistro_local_branches', serialized);
  } catch (e) {
    console.warn('[LocalStore] saveLocalBranches error:', e);
  }
}

export function getLocalInventory(branchId?: string): CatalogItem[] {
  if (typeof localStorage === 'undefined') return [];
  const targetBranch = branchId || 'branch-1792458194300-3i4l';
  try {
    // 1. Branch catalog
    const branchCat = localStorage.getItem(`${CATALOG_STORAGE_PREFIX}${targetBranch}`);
    if (branchCat) {
      const parsed = JSON.parse(branchCat);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
    // 2. Global inventory
    const inv = localStorage.getItem('bistro_inventory');
    if (inv) {
      const parsed = JSON.parse(inv);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
    // 3. cache_inventory
    const cInv = localStorage.getItem('cache_inventory');
    if (cInv) {
      const parsed = JSON.parse(cInv);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
    // 4. Any branch catalog in storage
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(CATALOG_STORAGE_PREFIX)) {
        const raw = localStorage.getItem(key);
        if (raw) {
          const p = JSON.parse(raw);
          if (Array.isArray(p) && p.length > 0) return p;
        }
      }
    }
  } catch (e) {
    console.warn('[LocalStore] getLocalInventory error:', e);
  }
  return [];
}

export function saveLocalInventory(branchId: string, items: CatalogItem[]): void {
  if (typeof localStorage === 'undefined' || !Array.isArray(items)) return;
  const targetBranch = branchId || 'branch-1792458194300-3i4l';
  try {
    const serialized = JSON.stringify(items);
    localStorage.setItem(`${CATALOG_STORAGE_PREFIX}${targetBranch}`, serialized);
    localStorage.setItem('bistro_inventory', serialized);
    localStorage.setItem('cache_inventory', serialized);
  } catch (e) {
    console.warn('[LocalStore] saveLocalInventory error:', e);
  }
}


export class OfflineSyncService {
  private static instance: OfflineSyncService;
  private dbPromise: Promise<IDBDatabase | null> | null = null;
  private isSyncing = false;
  private syncTimer: any = null;
  private healthCheckTimer: any = null;
  private retryBackoffMs = 3000;
  private isOnline = typeof navigator !== 'undefined' ? navigator.onLine : true;

  private constructor() {
    this.initIndexedDB();
    this.setupNetworkListeners();
    this.startPeriodicSync();
  }

  public static getInstance(): OfflineSyncService {
    if (!OfflineSyncService.instance) {
      OfflineSyncService.instance = new OfflineSyncService();
    }
    return OfflineSyncService.instance;
  }

  // =========================================================================
  // 1. DUAL-LAYER STORAGE ENGINE (IndexedDB + LocalStorage Fallback)
  // =========================================================================

  private initIndexedDB(): Promise<IDBDatabase | null> {
    if (this.dbPromise) return this.dbPromise;
    if (typeof window === 'undefined' || !window.indexedDB) {
      this.dbPromise = Promise.resolve(null);
      return this.dbPromise;
    }

    this.dbPromise = new Promise((resolve) => {
      try {
        const req = window.indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = (e: any) => {
          const db = e.target.result as IDBDatabase;
          if (!db.objectStoreNames.contains('sync_queue')) {
            const store = db.createObjectStore('sync_queue', { keyPath: 'id' });
            store.createIndex('client_created_at', 'client_created_at', { unique: false });
            store.createIndex('status', 'status', { unique: false });
          }
          if (!db.objectStoreNames.contains('local_catalog')) {
            db.createObjectStore('local_catalog', { keyPath: 'id' });
          }
          if (!db.objectStoreNames.contains('local_shifts')) {
            db.createObjectStore('local_shifts', { keyPath: 'id' });
          }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => {
          console.warn('[OfflineSync] IndexedDB open error, using LocalStorage fallback');
          resolve(null);
        };
      } catch (err) {
        console.warn('[OfflineSync] IndexedDB init exception:', err);
        resolve(null);
      }
    });

    return this.dbPromise;
  }

  // =========================================================================
  // 2. NETWORK MONITORING & CONNECTIVITY PING
  // =========================================================================

  private setupNetworkListeners(): void {
    if (typeof window === 'undefined') return;

    window.addEventListener('online', async () => {
      console.log('[OfflineSync] Evento "online" recibido. Verificando conexión real...');
      await this.checkRealConnection();
      if (this.isOnline) {
        this.flushQueue();
      }
    });

    window.addEventListener('offline', () => {
      console.warn('[OfflineSync] Evento "offline" recibido. Cambiando a modo Offline...');
      this.isOnline = false;
      this.notifyStatusChange('Modo offline activo (sin señal de red)');
    });

    // Check actual connection on boot
    this.checkRealConnection();
  }

  public async checkRealConnection(): Promise<boolean> {
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      this.isOnline = false;
      this.notifyStatusChange();
      return false;
    }

    try {
      // Lightweight probe to verify actual end-to-end internet connectivity
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4000);
      const res = await fetch(`${SUPABASE_URL}/rest/v1/`, {
        method: 'HEAD',
        headers: { apikey: SUPABASE_ANON_KEY },
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      this.isOnline = res.ok || res.status < 500;
    } catch {
      this.isOnline = false;
    }

    this.notifyStatusChange();
    return this.isOnline;
  }

  private startPeriodicSync(): void {
    if (typeof window === 'undefined') return;

    // Periodic queue flush every 15 seconds if online
    this.syncTimer = setInterval(async () => {
      const queue = await this.getSyncQueue();
      if (queue.length > 0 && this.isOnline && !this.isSyncing) {
        this.flushQueue();
      }
    }, 15000);

    // Periodic connectivity ping every 30 seconds
    this.healthCheckTimer = setInterval(() => {
      this.checkRealConnection();
    }, 30000);
  }

  // =========================================================================
  // 3. LOCAL CATALOG MANAGEMENT & PRE-EMPTIVE STOCK DEDUCTION
  // =========================================================================

  public async getLocalCatalog(branchId: string): Promise<CatalogItem[]> {
    const key = `${CATALOG_STORAGE_PREFIX}${branchId}`;
    try {
      const raw = localStorage.getItem(key);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}

    const db = await this.initIndexedDB();
    if (db) {
      return new Promise((resolve) => {
        try {
          const tx = db.transaction('local_catalog', 'readonly');
          const store = tx.objectStore('local_catalog');
          const req = store.getAll();
          req.onsuccess = () => {
            const items = req.result || [];
            const filtered = items.filter((it: any) => !it.branch_id || it.branch_id === branchId);
            resolve(filtered);
          };
          req.onerror = () => resolve([]);
        } catch {
          resolve([]);
        }
      });
    }

    return [];
  }

  public async saveLocalCatalog(branchId: string, items: CatalogItem[]): Promise<void> {
    const key = `${CATALOG_STORAGE_PREFIX}${branchId}`;
    try {
      localStorage.setItem(key, JSON.stringify(items));
    } catch (e) {
      console.warn('[OfflineSync] LocalStorage save catalog quota notice:', e);
    }

    const db = await this.initIndexedDB();
    if (db && Array.isArray(items)) {
      try {
        const tx = db.transaction('local_catalog', 'readwrite');
        const store = tx.objectStore('local_catalog');
        items.forEach(it => {
          store.put({ ...it, branch_id: branchId });
        });
      } catch {}
    }

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('bistro_catalog_updated', { detail: { branchId, count: items.length } }));
    }
  }

  /**
   * Decrements stock in local catalog IMMEDIATELY so POS never allows overselling
   */
  public async decrementLocalStock(
    branchId: string,
    deductions: { itemId: string; quantity: number }[]
  ): Promise<void> {
    if (!deductions || deductions.length === 0) return;

    const catalog = await this.getLocalCatalog(branchId);
    let modified = false;

    deductions.forEach(ded => {
      const target = catalog.find(
        it => it.id === ded.itemId || it.item_id === ded.itemId
      );
      if (target) {
        const current = Number(target.current_stock ?? target.stock ?? 0);
        const newStock = Math.max(0, current - Number(ded.quantity || 0));
        target.current_stock = newStock;
        target.stock = newStock;
        modified = true;
      }
    });

    if (modified) {
      await this.saveLocalCatalog(branchId, catalog);
    }
  }

  // =========================================================================
  // 4. SYNC QUEUE MANAGEMENT (Strict FIFO Order)
  // =========================================================================

  public async getSyncQueue(): Promise<SyncQueueItem[]> {
    try {
      const raw = localStorage.getItem(QUEUE_STORAGE_KEY);
      if (raw) {
        const list = JSON.parse(raw);
        if (Array.isArray(list)) {
          return list.sort((a, b) => 
            new Date(a.client_created_at).getTime() - new Date(b.client_created_at).getTime()
          );
        }
      }
    } catch {}

    return [];
  }

  private persistQueue(queue: SyncQueueItem[]): void {
    try {
      localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
    } catch (e) {
      console.error('[OfflineSync] Error saving queue to localStorage:', e);
    }
    this.notifyStatusChange();
  }

  public async enqueueOperation(
    op: Omit<SyncQueueItem, 'id' | 'client_created_at' | 'status' | 'retry_count'>
  ): Promise<SyncQueueItem> {
    const queue = await this.getSyncQueue();
    const id = typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `queue-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

    const newItem: SyncQueueItem = {
      id,
      action: op.action,
      table: op.table,
      payload: op.payload,
      client_created_at: new Date().toISOString(),
      status: 'pending',
      retry_count: 0
    };

    queue.push(newItem);
    this.persistQueue(queue);

    // If online, immediately trigger background flush
    if (this.isOnline && !this.isSyncing) {
      this.flushQueue();
    }

    return newItem;
  }

  public async updateQueueItem(id: string, updates: Partial<SyncQueueItem>): Promise<void> {
    const queue = await this.getSyncQueue();
    const idx = queue.findIndex(item => item.id === id);
    if (idx !== -1) {
      queue[idx] = { ...queue[idx], ...updates };
      this.persistQueue(queue);
    }
  }

  public async removeQueueItem(id: string): Promise<void> {
    let queue = await this.getSyncQueue();
    queue = queue.filter(item => item.id !== id);
    this.persistQueue(queue);
  }

  // =========================================================================
  // 5. CHRONOLOGICAL SYNC ENGINE (Flush Queue FIFO with Exponential Backoff)
  // =========================================================================

  public async flushQueue(): Promise<{ processed: number; failed: number }> {
    if (this.isSyncing) return { processed: 0, failed: 0 };
    
    // Quick pre-check
    const isActuallyOnline = await this.checkRealConnection();
    if (!isActuallyOnline) {
      console.log('[OfflineSync] Sin conexión verificada. Sincronización en pausa.');
      return { processed: 0, failed: 0 };
    }

    const queue = await this.getSyncQueue();
    if (queue.length === 0) {
      return { processed: 0, failed: 0 };
    }

    this.isSyncing = true;
    this.notifyStatusChange('Sincronizando operaciones...');
    let processed = 0;
    let failed = 0;

    try {
      // Process items one by one strictly FIFO
      for (const item of queue) {
        await this.updateQueueItem(item.id, { status: 'syncing' });

        try {
          const success = await this.dispatchOperation(item);
          if (success) {
            await this.removeQueueItem(item.id);
            processed++;
            // Reset backoff on successful step
            this.retryBackoffMs = 3000;
          } else {
            failed++;
            await this.updateQueueItem(item.id, {
              status: 'failed',
              retry_count: (item.retry_count || 0) + 1,
              last_error: 'Rechazado por el servidor'
            });
            // Stop loop on error to preserve strict chronological ordering
            console.warn('[OfflineSync] Falló operación en cola. Pausando para preservar orden cronológico.');
            break;
          }
        } catch (err: any) {
          failed++;
          const errMsg = err?.message || String(err);
          console.error('[OfflineSync] Error de red ejecutando operación:', errMsg);

          await this.updateQueueItem(item.id, {
            status: 'failed',
            retry_count: (item.retry_count || 0) + 1,
            last_error: errMsg
          });

          // Exponential backoff
          this.retryBackoffMs = Math.min(this.retryBackoffMs * 2, 30000);
          setTimeout(() => {
            if (this.isOnline && !this.isSyncing) {
              this.flushQueue();
            }
          }, this.retryBackoffMs);

          break; // Stop execution to guarantee FIFO
        }
      }

      // Delta sync if queue was fully flushed
      const remaining = await this.getSyncQueue();
      if (remaining.length === 0) {
        const activeBranch = localStorage.getItem('bistro_selected_branch_id') || 'branch-1792458194300-3i4l';
        await this.reconcileDelta(activeBranch);
      }
    } finally {
      this.isSyncing = false;
      this.notifyStatusChange(
        processed > 0 ? `${processed} operación(es) sincronizada(s)` : undefined
      );
    }

    return { processed, failed };
  }

  /**
   * Dispatches a single operation to Supabase based on action type
   */
  private async dispatchOperation(item: SyncQueueItem): Promise<boolean> {
    switch (item.action) {
      case 'SALE': {
        const sale = item.payload.sale;
        const branchId = item.payload.branchId || sale.branchId || sale.branch_id;
        const tenantId = item.payload.tenantId || sale.tenant_id || 'biz-main';

        const salePayload = {
          id: sale.id,
          tenant_id: tenantId,
          branch_id: branchId,
          sale_number: sale.saleNumber || sale.sale_number,
          date: sale.date,
          time: sale.time,
          subtotal: sale.subtotal || sale.totalAmount || 0,
          tax_amount: sale.taxAmount || 0,
          tip_amount: sale.tipAmount || 0,
          total_amount: sale.totalAmount || sale.amountCUP || 0,
          payment_method: sale.paymentMethod || 'Efectivo',
          status: sale.status || 'completed',
          data: sale
        };

        // 1. Insert sale record
        const { error: saleErr } = await supabase
          .from('sales')
          .upsert(salePayload, { onConflict: 'id' });

        if (saleErr) {
          throw new Error(`Error en tabla sales: ${saleErr.message}`);
        }

        // 2. Decrement stock in Supabase branch_inventory
        const deductions = item.payload.deductions || [];
        for (const ded of deductions) {
          try {
            const { data: bRow } = await supabase
              .from('branch_inventory')
              .select('id, current_stock')
              .eq('branch_id', branchId)
              .eq('item_id', ded.id)
              .order('updated_at', { ascending: false })
              .limit(1)
              .maybeSingle();

            if (bRow?.id) {
              const currentDbStock = Number(bRow.current_stock || 0);
              const targetStock = ded.newBranchStock !== undefined
                ? ded.newBranchStock
                : Math.max(0, currentDbStock - (ded.quantity || 1));

              await supabase
                .from('branch_inventory')
                .update({
                  current_stock: targetStock,
                  updated_at: new Date().toISOString()
                })
                .eq('id', bRow.id);
            }
          } catch (stkErr) {
            console.warn('[OfflineSync] Advertencia actualizando branch_inventory:', stkErr);
          }
        }

        return true;
      }

      case 'SHIFT_START':
      case 'SHIFT_END': {
        const shift = item.payload;
        const { error } = await supabase
          .from('work_shifts')
          .upsert(shift, { onConflict: 'id' });

        if (error) throw new Error(`Error en work_shifts: ${error.message}`);
        return true;
      }

      case 'IPV_SUBMIT': {
        const report = item.payload;
        const { error } = await supabase
          .from('ipv_reports')
          .upsert(report, { onConflict: 'id' });

        if (error) throw new Error(`Error en ipv_reports: ${error.message}`);
        return true;
      }

      case 'PRODUCTION_BATCH':
      case 'BATCH_PRODUCTION': {
        const { branchId, productId, quantityProduced, deductions, userId, companyId } = item.payload;
        // 1. Try invoking the database RPC function directly
        const { data, error } = await supabase.rpc('register_batch_production', {
          p_branch_id: branchId,
          p_product_id: productId,
          p_quantity_produced: quantityProduced,
          p_user_id: userId || '00000000-0000-0000-0000-000000000000',
          p_company_id: companyId || 'biz-main'
        });

        if (!error && data) {
          if (data.success) return true;
          throw new Error(data.error || 'Error en procedimiento de lote');
        }

        // 2. If RPC is pending execution in Supabase, perform direct table synchronization
        if (error && (error.code === 'PGRST202' || error.message?.includes('schema cache') || error.code === '42703')) {
          console.warn('[OfflineSync] Aplicando sincronización directa de lote (insumos, sub-elaboraciones y elaborado) en Supabase');
          const nowIso = new Date().toISOString();

          if (Array.isArray(deductions)) {
            for (const ded of deductions) {
              const cleanDedId = String(ded.id || '').replace(/^(inv_|ing_)/, '');
              const qtyDed = Math.abs(Number(ded.quantity || 0));
              if (!cleanDedId || qtyDed <= 0) continue;

              const { data: dedBrRow } = await supabase
                .from('branch_inventory')
                .select('id, current_stock')
                .eq('branch_id', branchId)
                .eq('item_id', cleanDedId)
                .maybeSingle();

              if (dedBrRow?.id) {
                await supabase
                  .from('branch_inventory')
                  .update({
                    current_stock: Math.max(0, Number(dedBrRow.current_stock || 0) - qtyDed),
                    updated_at: nowIso
                  })
                  .eq('id', dedBrRow.id);
              }
            }
          }

          const { data: bRow } = await supabase
            .from('branch_inventory')
            .select('id, current_stock')
            .eq('branch_id', branchId)
            .eq('item_id', productId)
            .maybeSingle();

          if (bRow?.id) {
            await supabase.from('branch_inventory').update({
              current_stock: Number(bRow.current_stock || 0) + Number(quantityProduced),
              updated_at: nowIso
            }).eq('id', bRow.id);
          } else {
            await supabase.from('branch_inventory').insert({
              branch_id: branchId,
              item_id: productId,
              tenant_id: companyId || 'biz-main',
              current_stock: Number(quantityProduced),
              min_stock: 0,
              updated_at: nowIso
            });
          }
          return true;
        }

        if (error) throw new Error(`Error en producción: ${error.message}`);
        return true;
      }

      default:
        console.warn('[OfflineSync] Acción no reconocida:', item.action);
        return true;
    }
  }

  // =========================================================================
  // 6. DELTA SYNC & RECONCILIATION
  // =========================================================================

  public async reconcileDelta(branchId: string): Promise<void> {
    if (!this.isOnline) return;

    const timestampKey = `${LAST_SYNC_PREFIX}${branchId}`;
    const lastTimestamp = localStorage.getItem(timestampKey);

    try {
      let query = supabase
        .from('branch_inventory')
        .select(`
          id,
          branch_id,
          item_id,
          current_stock,
          min_stock,
          updated_at,
          inventory:item_id (
            id,
            name,
            category,
            selling_price_cup,
            selling_price_usd,
            barcode,
            sku,
            unit,
            active,
            status
          )
        `)
        .eq('branch_id', branchId)
        .order('updated_at', { ascending: false });

      if (lastTimestamp) {
        query = query.gt('updated_at', lastTimestamp);
      }

      const { data, error } = await query;
      if (error || !Array.isArray(data)) return;

      if (data.length > 0) {
        const catalog = await this.getLocalCatalog(branchId);
        const catalogMap = new Map(catalog.map(it => [it.id || it.item_id, it]));

        data.forEach(row => {
          const inv = (row as any).inventory || {};
          const itemId = row.item_id || inv.id;
          if (!itemId) return;

          const price = Number(inv.selling_price_cup || 100);
          const stock = Number(row.current_stock || 0);

          catalogMap.set(itemId, {
            id: itemId,
            item_id: itemId,
            name: inv.name || `Producto ${itemId}`,
            category: inv.category || 'Sellados / Enlatados',
            price,
            selling_price_cup: price,
            selling_price_usd: Number(inv.selling_price_usd || 0),
            current_stock: stock,
            stock,
            min_stock: Number(row.min_stock || 1),
            unit: inv.unit || 'uds',
            sku: inv.sku || '',
            barcode: inv.barcode || '',
            productType: inv.product_type || 'sealed_canned',
            active: inv.active !== false,
            branch_id: branchId,
            updated_at: row.updated_at
          });
        });

        await this.saveLocalCatalog(branchId, Array.from(catalogMap.values()));
      }

      localStorage.setItem(timestampKey, new Date().toISOString());
    } catch (err) {
      console.warn('[OfflineSync] Error reconciliando delta sync:', err);
    }
  }

  // =========================================================================
  // 7. STATUS & REACT NOTIFICATIONS
  // =========================================================================

  public async getStatus(): Promise<SyncEngineStatus> {
    const queue = await this.getSyncQueue();
    const count = queue.length;
    const activeBranch = (typeof localStorage !== 'undefined' && localStorage.getItem('bistro_selected_branch_id')) || 'branch-1792458194300-3i4l';
    const lastSync = typeof localStorage !== 'undefined' ? localStorage.getItem(`${LAST_SYNC_PREFIX}${activeBranch}`) : null;

    let state: SyncEngineStatus['state'] = 'online_synced';
    if (this.isSyncing) {
      state = 'syncing';
    } else if (!this.isOnline || count > 0) {
      state = 'offline_pending';
    }

    return {
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      pendingCount: count,
      lastSyncTimestamp: lastSync,
      state
    };
  }

  private async notifyStatusChange(message?: string): Promise<void> {
    if (typeof window === 'undefined') return;

    const status = await this.getStatus();
    if (message) status.message = message;

    window.dispatchEvent(new CustomEvent(SYNC_EVENT_NAME, { detail: status }));
  }
}

export const offlineSync = OfflineSyncService.getInstance();
