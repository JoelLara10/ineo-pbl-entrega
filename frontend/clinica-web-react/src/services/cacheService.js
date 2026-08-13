// src/services/cacheService.js
import AsyncStorage from '@react-native-async-storage/async-storage';

const CACHE_PREFIX = '@ineo_cache_';
const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutos en milisegundos

class CacheService {
  // Guardar datos en caché
  static async set(key, data, ttl = DEFAULT_TTL) {
    try {
      const item = {
        data: data,
        timestamp: Date.now(),
        ttl: ttl,
      };
      await AsyncStorage.setItem(CACHE_PREFIX + key, JSON.stringify(item));
      return true;
    } catch (error) {
      console.error('Error saving to cache:', error);
      return false;
    }
  }

  // Obtener datos de caché
  static async get(key) {
    try {
      const item = await AsyncStorage.getItem(CACHE_PREFIX + key);
      if (!item) return null;
      
      const parsed = JSON.parse(item);
      const now = Date.now();
      
      // Verificar si expiró
      if (now - parsed.timestamp > parsed.ttl) {
        await AsyncStorage.removeItem(CACHE_PREFIX + key);
        return null;
      }
      
      return parsed.data;
    } catch (error) {
      console.error('Error reading from cache:', error);
      return null;
    }
  }

  // Eliminar un item específico
  static async remove(key) {
    try {
      await AsyncStorage.removeItem(CACHE_PREFIX + key);
      return true;
    } catch (error) {
      console.error('Error removing from cache:', error);
      return false;
    }
  }

  // Limpiar toda la caché
  static async clear() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(CACHE_PREFIX));
      await AsyncStorage.multiRemove(cacheKeys);
      return true;
    } catch (error) {
      console.error('Error clearing cache:', error);
      return false;
    }
  }

  // Limpiar caché expirada
  static async cleanExpired() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(CACHE_PREFIX));
      
      for (const key of cacheKeys) {
        const item = await AsyncStorage.getItem(key);
        if (item) {
          const parsed = JSON.parse(item);
          const now = Date.now();
          if (now - parsed.timestamp > parsed.ttl) {
            await AsyncStorage.removeItem(key);
          }
        }
      }
      return true;
    } catch (error) {
      console.error('Error cleaning expired cache:', error);
      return false;
    }
  }

  // Obtener estadísticas de caché
  static async getStats() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(CACHE_PREFIX));
      let totalSize = 0;
      let expiredCount = 0;
      
      for (const key of cacheKeys) {
        const item = await AsyncStorage.getItem(key);
        if (item) {
          totalSize += item.length;
          const parsed = JSON.parse(item);
          const now = Date.now();
          if (now - parsed.timestamp > parsed.ttl) {
            expiredCount++;
          }
        }
      }
      
      return {
        totalItems: cacheKeys.length,
        expiredItems: expiredCount,
        totalSizeKB: Math.round(totalSize / 1024),
      };
    } catch (error) {
      console.error('Error getting cache stats:', error);
      return null;
    }
  }
}

export default CacheService;