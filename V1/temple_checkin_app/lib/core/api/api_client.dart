import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_endpoints.dart';
import 'api_exceptions.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  late Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  void initialize() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiEndpoints.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _setupInterceptors();
  }

  void _setupInterceptors() {
    // Request interceptor - 加入 JWT token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'jwt_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        print('Request: ${options.method} ${options.path}');
        handler.next(options);
      },
      onResponse: (response, handler) {
        print(
            'Response: ${response.statusCode} ${response.requestOptions.path}');
        handler.next(response);
      },
      onError: (error, handler) async {
        print('Error: ${error.response?.statusCode} ${error.message}');

        // 如果是 401 錯誤，嘗試刷新 token
        if (error.response?.statusCode == 401) {
          try {
            await _refreshToken();
            // 重新發送原始請求
            final newRequest = await _dio.fetch(error.requestOptions);
            return handler.resolve(newRequest);
          } catch (e) {
            // 刷新失敗，清除 token 並導向登入頁面
            await _clearTokens();
            return handler.next(error);
          }
        }

        handler.next(error);
      },
    ));
  }

  // GET 請求
  Future<Response> get(String endpoint, {Map<String, dynamic>? params}) async {
    try {
      final response = await _dio.get(endpoint, queryParameters: params);
      return response;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // POST 請求
  Future<Response> post(String endpoint, {dynamic data}) async {
    try {
      final response = await _dio.post(endpoint, data: data);
      return response;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // PUT 請求
  Future<Response> put(String endpoint, {dynamic data}) async {
    try {
      final response = await _dio.put(endpoint, data: data);
      return response;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // DELETE 請求
  Future<Response> delete(String endpoint) async {
    try {
      final response = await _dio.delete(endpoint);
      return response;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // 設定 JWT Token
  Future<void> setToken(String token) async {
    await _storage.write(key: 'jwt_token', value: token);
  }

  // 獲取 JWT Token
  Future<String?> getToken() async {
    return await _storage.read(key: 'jwt_token');
  }

  // 刷新 Token
  Future<void> _refreshToken() async {
    final refreshToken = await _storage.read(key: 'refresh_token');
    if (refreshToken == null) {
      throw ApiException('No refresh token available');
    }

    final response = await _dio.post(
      ApiEndpoints.refreshToken,
      data: {'refresh_token': refreshToken},
    );

    final newToken = response.data['access_token'];
    await setToken(newToken);
  }

  // 清除 Tokens
  Future<void> _clearTokens() async {
    await _storage.delete(key: 'jwt_token');
    await _storage.delete(key: 'refresh_token');
  }

  // 登出
  Future<void> logout() async {
    await _clearTokens();
  }

  // 處理 Dio 錯誤
  ApiException _handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException('連線逾時，請檢查網路連線');
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final message = error.response?.data['message'] ?? '伺服器錯誤';
        return ApiException('$message (錯誤代碼: $statusCode)');
      case DioExceptionType.cancel:
        return ApiException('請求已取消');
      case DioExceptionType.unknown:
        return ApiException('網路連線失敗，請檢查網路設定');
      default:
        return ApiException('未知錯誤');
    }
  }
}
