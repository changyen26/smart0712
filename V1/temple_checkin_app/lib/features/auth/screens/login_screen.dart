import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_constants.dart';
import '../../../shared/widgets/custom_button.dart';
import '../../../shared/widgets/custom_text_field.dart';
import '../../../shared/widgets/loading_widget.dart';
import '../providers/auth_provider.dart';
import 'register_screen.dart';
import '../../home/screens/home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  // 表單驗證
  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return '請輸入電子郵件';
    }
    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
      return '請輸入有效的電子郵件格式';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return '請輸入密碼';
    }
    if (value.length < AppConstants.minPasswordLength) {
      return '密碼至少需要 ${AppConstants.minPasswordLength} 個字元';
    }
    return null;
  }

  // 執行登入
  Future<void> _handleLogin() async {
    if (_formKey.currentState?.validate() ?? false) {
      final authProvider = context.read<AuthProvider>();

      final success = await authProvider.login(
        _emailController.text.trim(),
        _passwordController.text,
      );

      if (mounted) {
        if (success) {
          // 登入成功，導向首頁
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const HomeScreen()),
          );
        } else {
          // 顯示錯誤訊息
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(authProvider.errorMessage ?? '登入失敗'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
    }
  }

  // 導向註冊頁面
  void _navigateToRegister() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (context) => const RegisterScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return LoadingOverlay(
            isLoading: authProvider.isLoading,
            loadingMessage: '登入中...',
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: 60),

                      // Logo 和標題
                      _buildHeader(),

                      const SizedBox(height: 48),

                      // 登入表單
                      _buildLoginForm(),

                      const SizedBox(height: 24),

                      // 登入按鈕
                      CustomButton(
                        text: '登入',
                        onPressed: authProvider.isLoading ? null : _handleLogin,
                        isFullWidth: true,
                        isLoading: authProvider.isLoading,
                      ),

                      const SizedBox(height: 16),

                      // 忘記密碼
                      _buildForgotPassword(),

                      const SizedBox(height: 32),

                      // 分隔線
                      _buildDivider(),

                      const SizedBox(height: 32),

                      // 註冊按鈕
                      _buildRegisterSection(),

                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        // Logo
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: AppColors.primary,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withValues(alpha: 0.3),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: const Icon(
            Icons.temple_buddhist,
            size: 50,
            color: AppColors.onPrimary,
          ),
        ),
        const SizedBox(height: 24),

        // 標題
        Text(
          '歡迎回來',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.onBackground,
              ),
        ),
        const SizedBox(height: 8),

        // 副標題
        Text(
          '請登入您的帳戶以繼續使用',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.onSurfaceVariant,
              ),
        ),
      ],
    );
  }

  Widget _buildLoginForm() {
    return Column(
      children: [
        // 電子郵件欄位
        CustomTextField(
          label: '電子郵件',
          hint: '請輸入您的電子郵件',
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          prefixIcon: Icons.email_outlined,
          validator: _validateEmail,
        ),
        const SizedBox(height: 16),

        // 密碼欄位
        CustomTextField(
          label: '密碼',
          hint: '請輸入您的密碼',
          controller: _passwordController,
          obscureText: true,
          prefixIcon: Icons.lock_outlined,
          validator: _validatePassword,
        ),
      ],
    );
  }

  Widget _buildForgotPassword() {
    return Align(
      alignment: Alignment.centerRight,
      child: TextButton(
        onPressed: () {
          // TODO: 實作忘記密碼功能
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('忘記密碼功能開發中...')),
          );
        },
        child: const Text(
          '忘記密碼？',
          style: TextStyle(
            color: AppColors.primary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  Widget _buildDivider() {
    return Row(
      children: [
        const Expanded(child: Divider()),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            '或',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.onSurfaceVariant,
                ),
          ),
        ),
        const Expanded(child: Divider()),
      ],
    );
  }

  Widget _buildRegisterSection() {
    return Column(
      children: [
        Text(
          '還沒有帳戶嗎？',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: 8),
        CustomButton(
          text: '註冊新帳戶',
          onPressed: _navigateToRegister,
          type: ButtonType.outline,
          isFullWidth: true,
        ),
      ],
    );
  }
}
