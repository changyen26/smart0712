import 'package:flutter/material.dart';

class AppColors {
  // 主色調
  static const Color primary = Color(0xFFD32F2F); // 廟宇紅色
  static const Color primaryLight = Color(0xFFFFCDD2);
  static const Color primaryDark = Color(0xFFB71C1C);

  // 次要色調
  static const Color secondary = Color(0xFFFFB300); // 金色
  static const Color secondaryLight = Color(0xFFFFF8E1);
  static const Color secondaryDark = Color(0xFFF57F17);

  // 中性色
  static const Color background = Color(0xFFFAFAFA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF5F5F5);

  // 文字顏色
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color onSecondary = Color(0xFF000000);
  static const Color onBackground = Color(0xFF1C1B1F);
  static const Color onSurface = Color(0xFF1C1B1F);
  static const Color onSurfaceVariant = Color(0xFF49454F);

  // 功能性顏色
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);

  // 福報相關顏色
  static const Color blessing = Color(0xFFFFB300); // 金色
  static const Color blessingGradientStart = Color(0xFFFFD700);
  static const Color blessingGradientEnd = Color(0xFFFF8F00);

  // 廟宇相關顏色
  static const Color temple = Color(0xFFD32F2F); // 廟宇紅
  static const Color templeAccent = Color(0xFFBF360C); // 深橘紅

  // 成就顏色
  static const Color achievement = Color(0xFF9C27B0); // 紫色
  static const Color achievementGold = Color(0xFFFFD700); // 金色成就
  static const Color achievementSilver = Color(0xFFC0C0C0); // 銀色成就
  static const Color achievementBronze = Color(0xFFCD7F32); // 銅色成就

  // 狀態顏色
  static const Color active = Color(0xFF4CAF50);
  static const Color inactive = Color(0xFF9E9E9E);
  static const Color pending = Color(0xFFFF9800);

  // 陰影顏色
  static const Color shadow = Color(0x1A000000);
  static const Color shadowLight = Color(0x0D000000);

  // 漸層色
  static const List<Color> primaryGradient = [
    Color(0xFFD32F2F),
    Color(0xFFBF360C),
  ];

  static const List<Color> secondaryGradient = [
    Color(0xFFFFB300),
    Color(0xFFF57F17),
  ];

  static const List<Color> blessingGradient = [
    Color(0xFFFFD700),
    Color(0xFFFF8F00),
  ];

  // 取得福報等級顏色
  static Color getBlessingLevelColor(int level) {
    switch (level) {
      case 1:
        return const Color(0xFF8BC34A); // 綠色
      case 2:
        return const Color(0xFF2196F3); // 藍色
      case 3:
        return const Color(0xFF9C27B0); // 紫色
      case 4:
        return const Color(0xFFFF9800); // 橘色
      case 5:
        return const Color(0xFFF44336); // 紅色
      case 6:
        return const Color(0xFFFFD700); // 金色
      default:
        return const Color(0xFF9E9E9E); // 灰色
    }
  }

  // Material 3 主題
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        brightness: Brightness.light,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: primary,
        foregroundColor: onPrimary,
        elevation: 0,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: onPrimary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      cardTheme: const CardThemeData(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(12)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: primary, width: 2),
        ),
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        brightness: Brightness.dark,
      ),
    );
  }
}
