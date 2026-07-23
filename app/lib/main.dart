import 'package:flutter/material.dart';

import 'screens/birth_form_screen.dart';

void main() {
  runApp(const JyotishVedaApp());
}

class JyotishVedaApp extends StatelessWidget {
  const JyotishVedaApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF7A3E9D);
    return MaterialApp(
      title: 'JyotishVedaAI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.dark),
        useMaterial3: true,
      ),
      home: const BirthFormScreen(),
    );
  }
}
