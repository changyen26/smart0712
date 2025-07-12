import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_constants.dart';
import '../../../shared/widgets/custom_button.dart';
import '../../../shared/widgets/custom_text_field.dart';
import '../../../shared/widgets/loading_widget.dart';
import '../providers/auth_provider.dart';
import '../../home/screens/home_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _agreeToTerms = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  // 表單驗證
  String? _validateUsername(String? value) {
    if (value == null || value.isEmpty) {
      return '請輸入使用者名稱';
    }
    if (value.length < AppConstants.minUsernameLength) {
      return '使用者名稱至少需要 ${AppConstants.minUsernameLength} 個字元';
    }
    if (value.length > AppConstants.maxUsernameLength) {
      return '使用者名稱不能超過 ${AppConstants.maxUsernameLength} 個字元';
    }
    return null;
  }

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
    if (value.length > AppConstants.maxPasswordLength) {
      return '密碼不能超過 ${AppConstants.maxPasswordLength} 個字元';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return '請確認密碼';
    }
    if (value != _passwordController.text) {
      return '密碼確認不一致';
    }
    return null;
  }

  // 執行註冊
  Future<void> _handleRegister() async {
    if (_formKey.currentState?.validate() ?? false) {
      if (!_agreeToTerms) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('請先同意服務條款'),
            backgroundColor: AppColors.warning,
          ),
        );
        return;
      }

      final authProvider = context.read<AuthProvider>();

      final success = await authProvider.register(
        _usernameController.text.trim(),
        _emailController.text.trim(),
        _passwordController.text,
      );

      if (mounted) {
        if (success) {
          // 註冊成功，顯示歡迎訊息並導向首頁
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(AppConstants.successRegister),
              backgroundColor: AppColors.success,
            ),
          );

          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const HomeScreen()),
          );
        } else {
          // 顯示錯誤訊息
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(authProvider.errorMessage ?? '註冊失敗'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: AppColors.onBackground),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return LoadingOverlay(
            isLoading: authProvider.isLoading,
            loadingMessage: '註冊中...',
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // 標題
                      _buildHeader(),

                      const SizedBox(height: 32),

                      // 註冊表單
                      _buildRegisterForm(),

                      const SizedBox(height: 16),

                      // 服務條款同意
                      _buildTermsAgreement(),

                      const SizedBox(height: 24),

                      // 註冊按鈕
                      CustomButton(
                        text: '註冊帳戶',
                        onPressed:
                            authProvider.isLoading ? null : _handleRegister,
                        isFullWidth: true,
                        isLoading: authProvider.isLoading,
                      ),

                      const SizedBox(height: 16),

                      // 登入提示
                      _buildLoginPrompt(),

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
        Text(
          '建立新帳戶',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.onBackground,
              ),
        ),
        const SizedBox(height: 8),
        Text(
          '加入我們，開始您的福報之旅',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.onSurfaceVariant,
              ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildRegisterForm() {
    return Column(
      children: [
        // 使用者名稱欄位
        CustomTextField(
          label: '使用者名稱',
          hint: '請輸入使用者名稱',
          controller: _usernameController,
          prefixIcon: Icons.person_outlined,
          validator: _validateUsername,
          textCapitalization: TextCapitalization.words,
        ),
        const SizedBox(height: 16),

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
          hint: '請輸入密碼',
          controller: _passwordController,
          obscureText: true,
          prefixIcon: Icons.lock_outlined,
          validator: _validatePassword,
        ),
        const SizedBox(height: 16),

        // 確認密碼欄位
        CustomTextField(
          label: '確認密碼',
          hint: '請再次輸入密碼',
          controller: _confirmPasswordController,
          obscureText: true,
          prefixIcon: Icons.lock_outlined,
          validator: _validateConfirmPassword,
        ),
      ],
    );
  }

  Widget _buildTermsAgreement() {
    return Row(
      children: [
        Checkbox(
          value: _agreeToTerms,
          onChanged: (value) {
            setState(() {
              _agreeToTerms = value ?? false;
            });
          },
          activeColor: AppColors.primary,
        ),
        Expanded(
          child: GestureDetector(
            onTap: () {
              setState(() {
                _agreeToTerms = !_agreeToTerms;
              });
            },
            child: RichText(
              text: TextSpan(
                style: Theme.of(context).textTheme.bodyMedium,
                children: [
                  const TextSpan(text: '我已閱讀並同意 '),
                  TextSpan(
                    text: '服務條款',
                    style: TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const TextSpan(text: ' 和 '),
                  TextSpan(
                    text: '隱私政策',
                    style: TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLoginPrompt() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          '已經有帳戶了？ ',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.onSurfaceVariant,
              ),
        ),
        GestureDetector(
          onTap: () => Navigator.of(context).pop(),
          child: Text(
            '立即登入',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
      ],
    );
  }
}
