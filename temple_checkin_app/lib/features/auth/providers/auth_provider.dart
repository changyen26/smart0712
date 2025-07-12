import 'package:flutter/material.dart';
import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../../../core/api/api_exceptions.dart';
import '../../../core/models/user_model.dart';
import '../../../shared/utils/storage_utils.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated }

class AuthProvider with ChangeNotifier {
  AuthStatus _status = AuthStatus.initial;
  UserModel? _user;
  String? _errorMessage;

  AuthStatus get status => _status;
  UserModel? get user => _user;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _status == AuthStatus.authenticated;
  bool get isLoading => _status == AuthStatus.loading;

  final ApiClient _apiClient = ApiClient();

  // 初始化認證狀態
  Future<void> initialize() async {
    _setStatus(AuthStatus.loading);

    try {
      final token = await _apiClient.getToken();
      if (token != null) {
        // 驗證 token 是否有效
        await _validateToken();
      } else {
        _setStatus(AuthStatus.unauthenticated);
      }
    } catch (e) {
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  // 登入
  Future<bool> login(String email, String password) async {
    _setStatus(AuthStatus.loading);
    _clearError();

    try {
      final response = await _apiClient.post(
        ApiEndpoints.login,
        data: {
          'email': email,
          'password': password,
        },
      );

      final data = response.data;
      final token = data['access_token'];
      final userData = data['user'];

      // 儲存 token
      await _apiClient.setToken(token);

      // 儲存使用者資料
      _user = UserModel.fromJson(userData);
      await StorageUtils.saveUserData(_user!);

      _setStatus(AuthStatus.authenticated);
      return true;
    } on ApiException catch (e) {
      _setError(e.message);
      _setStatus(AuthStatus.unauthenticated);
      return false;
    } catch (e) {
      _setError('登入失敗，請稍後再試');
      _setStatus(AuthStatus.unauthenticated);
      return false;
    }
  }

  // 註冊
  Future<bool> register(String username, String email, String password) async {
    _setStatus(AuthStatus.loading);
    _clearError();

    try {
      final response = await _apiClient.post(
        ApiEndpoints.register,
        data: {
          'username': username,
          'email': email,
          'password': password,
        },
      );

      final data = response.data;
      final token = data['access_token'];
      final userData = data['user'];

      // 儲存 token
      await _apiClient.setToken(token);

      // 儲存使用者資料
      _user = UserModel.fromJson(userData);
      await StorageUtils.saveUserData(_user!);

      _setStatus(AuthStatus.authenticated);
      return true;
    } on ApiException catch (e) {
      _setError(e.message);
      _setStatus(AuthStatus.unauthenticated);
      return false;
    } catch (e) {
      _setError('註冊失敗，請稍後再試');
      _setStatus(AuthStatus.unauthenticated);
      return false;
    }
  }

  // 登出
  Future<void> logout() async {
    try {
      await _apiClient.post(ApiEndpoints.logout);
    } catch (e) {
      // 即使 API 呼叫失敗，也要清除本地資料
    }

    await _apiClient.logout();
    await StorageUtils.clearUserData();

    _user = null;
    _setStatus(AuthStatus.unauthenticated);
  }

  // 驗證 token
  Future<void> _validateToken() async {
    try {
      final response = await _apiClient.get(ApiEndpoints.userProfile);
      final userData = response.data['user'];

      _user = UserModel.fromJson(userData);
      await StorageUtils.saveUserData(_user!);

      _setStatus(AuthStatus.authenticated);
    } catch (e) {
      await _apiClient.logout();
      await StorageUtils.clearUserData();
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  // 更新使用者資料
  Future<bool> updateProfile({
    String? username,
    String? email,
    String? profileImage,
  }) async {
    if (_user == null) return false;

    try {
      final response = await _apiClient.put(
        ApiEndpoints.updateProfile,
        data: {
          if (username != null) 'username': username,
          if (email != null) 'email': email,
          if (profileImage != null) 'profile_image': profileImage,
        },
      );

      final userData = response.data['user'];
      _user = UserModel.fromJson(userData);
      await StorageUtils.saveUserData(_user!);

      notifyListeners();
      return true;
    } catch (e) {
      _setError('更新失敗，請稍後再試');
      return false;
    }
  }

  // 更新福報值
  void updateBlessingPoints(int points) {
    if (_user != null) {
      _user = _user!.copyWith(blessingPoints: _user!.blessingPoints + points);
      StorageUtils.saveUserData(_user!);
      notifyListeners();
    }
  }

  // 設定狀態
  void _setStatus(AuthStatus status) {
    _status = status;
    notifyListeners();
  }

  // 設定錯誤訊息
  void _setError(String message) {
    _errorMessage = message;
    notifyListeners();
  }

  // 清除錯誤訊息
  void _clearError() {
    _errorMessage = null;
  }
}
