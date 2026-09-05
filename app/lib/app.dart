import 'package:flutter/material.dart';

/// Root application widget for Finnapp.
class Finnapp extends StatelessWidget {
  const Finnapp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Finnapp',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF10B981), // Emerald green accent
          brightness: Brightness.light,
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF10B981),
          brightness: Brightness.dark,
        ),
      ),
      themeMode: ThemeMode.system,
      home: const _Sprint0PlaceholderScreen(),
    );
  }
}

class _Sprint0PlaceholderScreen extends StatelessWidget {
  const _Sprint0PlaceholderScreen();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.account_balance_wallet_outlined,
              size: 64,
              color: Color(0xFF10B981),
            ),
            SizedBox(height: 16),
            Text(
              'Finnapp',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                letterSpacing: -0.5,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Sistema Pessoal de Controle Financeiro',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
