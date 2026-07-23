import 'package:flutter_test/flutter_test.dart';

import 'package:jyotish_veda_app/main.dart';

void main() {
  testWidgets('Birth form screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(const JyotishVedaApp());

    expect(find.text('Your birth details'), findsOneWidget);
    expect(find.text('Get my reading'), findsOneWidget);
  });
}
