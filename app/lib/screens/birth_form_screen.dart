import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/api_service.dart';
import 'result_screen.dart';

class BirthFormScreen extends StatefulWidget {
  const BirthFormScreen({super.key});

  @override
  State<BirthFormScreen> createState() => _BirthFormScreenState();
}

class _BirthFormScreenState extends State<BirthFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _api = ApiService();

  final _nameController = TextEditingController();
  final _placeController = TextEditingController();
  final _questionController = TextEditingController();

  DateTime? _dateOfBirth;
  TimeOfDay? _timeOfBirth;
  bool _loading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _placeController.dispose();
    _questionController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _dateOfBirth ?? DateTime(now.year - 25),
      firstDate: DateTime(1900),
      lastDate: now,
    );
    if (picked != null) setState(() => _dateOfBirth = picked);
  }

  Future<void> _pickTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _timeOfBirth ?? const TimeOfDay(hour: 12, minute: 0),
    );
    if (picked != null) setState(() => _timeOfBirth = picked);
  }

  String get _formattedDate =>
      _dateOfBirth == null ? '' : DateFormat('yyyy-MM-dd').format(_dateOfBirth!);

  String get _formattedTime => _timeOfBirth == null
      ? ''
      : '${_timeOfBirth!.hour.toString().padLeft(2, '0')}:${_timeOfBirth!.minute.toString().padLeft(2, '0')}';

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_dateOfBirth == null || _timeOfBirth == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select both date and time of birth.')),
      );
      return;
    }

    setState(() => _loading = true);
    try {
      final result = await _api.consult(
        name: _nameController.text.trim(),
        placeOfBirth: _placeController.text.trim(),
        dateOfBirth: _formattedDate,
        timeOfBirth: _formattedTime,
        question: _questionController.text.trim(),
      );
      if (!mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('JyotishVedaAI')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Your birth details',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(
                  'Used to compute your Vedic birth chart.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Name',
                    prefixIcon: Icon(Icons.person_outline),
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Please enter your name' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _placeController,
                  decoration: const InputDecoration(
                    labelText: 'Place of birth',
                    hintText: 'e.g. Varanasi, Uttar Pradesh, India',
                    prefixIcon: Icon(Icons.location_on_outlined),
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Please enter place of birth' : null,
                ),
                const SizedBox(height: 16),
                InkWell(
                  onTap: _pickDate,
                  child: InputDecorator(
                    decoration: const InputDecoration(
                      labelText: 'Date of birth',
                      prefixIcon: Icon(Icons.calendar_today_outlined),
                      border: OutlineInputBorder(),
                    ),
                    child: Text(
                      _dateOfBirth == null ? 'Select date' : _formattedDate,
                      style: TextStyle(
                        color: _dateOfBirth == null ? Colors.grey[600] : null,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                InkWell(
                  onTap: _pickTime,
                  child: InputDecorator(
                    decoration: const InputDecoration(
                      labelText: 'Time of birth',
                      helperText: 'Local time at the place of birth, 24h',
                      prefixIcon: Icon(Icons.access_time),
                      border: OutlineInputBorder(),
                    ),
                    child: Text(
                      _timeOfBirth == null ? 'Select time' : _formattedTime,
                      style: TextStyle(
                        color: _timeOfBirth == null ? Colors.grey[600] : null,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _questionController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'Your question',
                    hintText: 'e.g. When will I get married?',
                    prefixIcon: Icon(Icons.help_outline),
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Please enter a question' : null,
                ),
                const SizedBox(height: 28),
                FilledButton.icon(
                  onPressed: _loading ? null : _submit,
                  icon: _loading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.auto_awesome),
                  label: Text(_loading ? 'Consulting...' : 'Get my reading'),
                  style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
