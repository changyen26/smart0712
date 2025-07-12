import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/constants/app_constants.dart';
import '../../core/models/user_model.dart';

class StorageUtils {
  static SharedPreferences? _prefs;

  // 初始化
  static Future<void> initialize() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  // 確保 SharedPreferences 已初始化
  static Future<SharedPreferences> _getPrefs() async {
    if (_prefs == null) {
      await initialize();
    }
    return _prefs!;
  }

  // 儲存使用者資料
  static Future<void> saveUserData(UserModel user) async {
    final prefs = await _getPrefs();
    final userJson = jsonEncode(user.toJson());
    await prefs.setString(AppConstants.keyUserData, userJson);
    await prefs.setString(AppConstants.keyUserId, user.id);
  }

  // 讀取使用者資料
  static Future<UserModel?> getUserData() async {
    final prefs = await _getPrefs();
    final userJson = prefs.getString(AppConstants.keyUserData);

    if (userJson != null) {
      try {
        final userMap = jsonDecode(userJson) as Map<String, dynamic>;
        return UserModel.fromJson(userMap);
      } catch (e) {
        // JSON 解析失敗，清除資料
        await clearUserData();
        return null;
      }
    }
    return null;
  }

  // 取得使用者 ID
  static Future<String?> getUserId() async {
    final prefs = await _getPrefs();
    return prefs.getString(AppConstants.keyUserId);
  }

  // 清除使用者資料
  static Future<void> clearUserData() async {
    final prefs = await _getPrefs();
    await prefs.remove(AppConstants.keyUserData);
    await prefs.remove(AppConstants.keyUserId);
  }

  // 儲存是否第一次開啟
  static Future<void> setFirstTime(bool isFirstTime) async {
    final prefs = await _getPrefs();
    await prefs.setBool(AppConstants.keyIsFirstTime, isFirstTime);
  }

  // 檢查是否第一次開啟
  static Future<bool> isFirstTime() async {
    final prefs = await _getPrefs();
    return prefs.getBool(AppConstants.keyIsFirstTime) ?? true;
  }

  // 儲存設定
  static Future<void> saveSetting(String key, dynamic value) async {
    final prefs = await _getPrefs();

    if (value is String) {
      await prefs.setString(key, value);
    } else if (value is int) {
      await prefs.setInt(key, value);
    } else if (value is double) {
      await prefs.setDouble(key, value);
    } else if (value is bool) {
      await prefs.setBool(key, value);
    } else if (value is List<String>) {
      await prefs.setStringList(key, value);
    } else {
      // 對於複雜物件，轉換為 JSON
      await prefs.setString(key, jsonEncode(value));
    }
  }

  // 讀取設定
  static Future<T?> getSetting<T>(String key) async {
    final prefs = await _getPrefs();

    if (T == String) {
      return prefs.getString(key) as T?;
    } else if (T == int) {
      return prefs.getInt(key) as T?;
    } else if (T == double) {
      return prefs.getDouble(key) as T?;
    } else if (T == bool) {
      return prefs.getBool(key) as T?;
    } else if (T == List<String>) {
      return prefs.getStringList(key) as T?;
    } else {
      // 對於複雜物件，從 JSON 解析
      final jsonString = prefs.getString(key);
      if (jsonString != null) {
        try {
          return jsonDecode(jsonString) as T?;
        } catch (e) {
          return null;
        }
      }
    }
    return null;
  }

  // 移除設定
  static Future<void> removeSetting(String key) async {
    final prefs = await _getPrefs();
    await prefs.remove(key);
  }

  // 清除所有設定
  static Future<void> clearAll() async {
    final prefs = await _getPrefs();
    await prefs.clear();
  }

  // 檢查鍵值是否存在
  static Future<bool> containsKey(String key) async {
    final prefs = await _getPrefs();
    return prefs.containsKey(key);
  }

  // 取得所有鍵值
  static Future<Set<String>> getAllKeys() async {
    final prefs = await _getPrefs();
    return prefs.getKeys();
  }
}
