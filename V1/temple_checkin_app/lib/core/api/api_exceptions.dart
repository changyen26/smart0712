class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? details;

  ApiException(this.message, {this.statusCode, this.details});

  @override
  String toString() {
    return 'ApiException: $message${statusCode != null ? ' (Status: $statusCode)' : ''}';
  }
}

class NetworkException extends ApiException {
  NetworkException(String message) : super(message);
}

class AuthenticationException extends ApiException {
  AuthenticationException(String message) : super(message, statusCode: 401);
}

class ValidationException extends ApiException {
  final Map<String, List<String>>? fieldErrors;

  ValidationException(String message, {this.fieldErrors})
      : super(message, statusCode: 422);
}

class ServerException extends ApiException {
  ServerException(String message) : super(message, statusCode: 500);
}

class NotFoundException extends ApiException {
  NotFoundException(String message) : super(message, statusCode: 404);
}
