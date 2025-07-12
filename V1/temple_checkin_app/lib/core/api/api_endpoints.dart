class ApiEndpoints {
  // 基礎 URL
  static const String baseUrl = 'http://localhost:5000/api';

  // 認證相關
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String refreshToken = '/auth/refresh';
  static const String logout = '/auth/logout';

  // 使用者相關
  static const String userProfile = '/users/profile';
  static const String updateProfile = '/users/profile';
  static const String deleteAccount = '/users/account';

  // 平安符相關
  static const String amulets = '/amulets';
  static const String createAmulet = '/amulets';
  static const String updateAmulet = '/amulets'; // + /{id}
  static const String deleteAmulet = '/amulets'; // + /{id}

  // 廟宇相關
  static const String temples = '/temples';
  static const String templeDetail = '/temples'; // + /{id}
  static const String nearbyTemples = '/temples/nearby';

  // 打卡相關
  static const String checkin = '/checkin';
  static const String checkinHistory = '/checkin/history';
  static const String checkinStats = '/checkin/stats';

  // 管理員相關
  static const String adminLogin = '/admin/login';
  static const String adminTemples = '/admin/temples';
  static const String adminStats = '/admin/stats';

  // 工具方法
  static String getTempleDetail(String id) => '$templeDetail/$id';
  static String getUpdateAmulet(String id) => '$updateAmulet/$id';
  static String getDeleteAmulet(String id) => '$deleteAmulet/$id';

  // 建構完整URL
  static String getFullUrl(String endpoint) => '$baseUrl$endpoint';
}
