import 'package:app/app.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Finnapp renders smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const Finnapp());

    // Verify Finnapp title and icon are present
    expect(find.text('Finnapp'), findsOneWidget);
    expect(
      find.text('Sistema Pessoal de Controle Financeiro'),
      findsOneWidget,
    );
    expect(find.byIcon(Icons.account_balance_wallet_outlined), findsOneWidget);
  });
}
