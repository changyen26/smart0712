class AppConstants {
  // 應用程式基本資訊
  static const String appName = '平安符打卡系統';
  static const String appVersion = '1.0.0';

  // 儲存鍵值
  static const String keyJwtToken = 'jwt_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserId = 'user_id';
  static const String keyUserData = 'user_data';
  static const String keyIsFirstTime = 'is_first_time';

  // 福報相關
  static const int defaultBlessingPoints = 1; // 預設打卡獲得的福報值
  static const int maxBlessingPointsPerDay = 10; // 每日最大福報值

  // 成就相關
  static const int achievementFirstCheckin = 1; // 第一次打卡
  static const int achievementStreak7Days = 7; // 連續打卡7天
  static const int achievementStreak30Days = 30; // 連續打卡30天
  static const int achievementVisit10Temples = 10; // 造訪10個不同廟宇
  static const int achievementVisit50Temples = 50; // 造訪50個不同廟宇
  static const int achievementBlessing100Points = 100; // 累積100福報值
  static const int achievementBlessing1000Points = 1000; // 累積1000福報值

  // 地圖相關
  static const double defaultLatitude = 24.1477; // 台中市緯度
  static const double defaultLongitude = 120.6736; // 台中市經度
  static const double searchRadius = 5000; // 搜尋半徑(公尺)

  // UI 相關
  static const double defaultPadding = 16.0;
  static const double defaultRadius = 8.0;
  static const double defaultElevation = 2.0;

  // 動畫時間
  static const int animationDurationMs = 300;
  static const int splashDelayMs = 2000;

  // 驗證規則
  static const int minPasswordLength = 6;
  static const int maxPasswordLength = 20;
  static const int minUsernameLength = 3;
  static const int maxUsernameLength = 20;

  // 錯誤訊息
  static const String errorNetworkConnection = '網路連線失敗，請檢查網路設定';
  static const String errorServerError = '伺服器發生錯誤，請稍後再試';
  static const String errorUnauthorized = '登入已過期，請重新登入';
  static const String errorValidation = '資料驗證失敗，請檢查輸入內容';
  static const String errorUnknown = '發生未知錯誤，請聯絡客服';

  // 成功訊息
  static const String successLogin = '登入成功';
  static const String successRegister = '註冊成功';
  static const String successCheckin = '打卡成功！';
  static const String successProfileUpdate = '個人資料更新成功';

  // 廟宇類型
  static const List<String> templeTypes = [
    '觀音廟',
    '媽祖廟',
    '關帝廟',
    '土地公廟',
    '城隍廟',
    '王爺廟',
    '玄天上帝廟',
    '天后宮',
    '三山國王廟',
    '保生大帝廟',
    '其他',
  ];

  // 福報等級
  static const List<Map<String, dynamic>> blessingLevels = [
    {'level': 1, 'name': '初心者', 'minPoints': 0, 'maxPoints': 99},
    {'level': 2, 'name': '虔誠信徒', 'minPoints': 100, 'maxPoints': 499},
    {'level': 3, 'name': '福報滿滿', 'minPoints': 500, 'maxPoints': 1499},
    {'level': 4, 'name': '功德圓滿', 'minPoints': 1500, 'maxPoints': 4999},
    {'level': 5, 'name': '大德高僧', 'minPoints': 5000, 'maxPoints': 9999},
    {'level': 6, 'name': '神通廣大', 'minPoints': 10000, 'maxPoints': -1},
  ];

  // 獲取福報等級
  static Map<String, dynamic> getBlessingLevel(int points) {
    for (var level in blessingLevels) {
      if (level['maxPoints'] == -1 || points <= level['maxPoints']) {
        return level;
      }
    }
    return blessingLevels.last; // 回傳最高等級
  }
}
