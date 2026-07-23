import 'package:flutter/material.dart';

import '../models/consult_result.dart';

class ResultScreen extends StatelessWidget {
  final ConsultResult result;

  const ResultScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final chart = result.chart;
    final currentDasha = chart.mahadasha.where((d) => d.current).toList();

    return Scaffold(
      appBar: AppBar(title: Text('${result.name}\'s Reading')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _SummaryCard(
              ascendantSign: chart.ascendant.sign,
              moonSign: chart.moonSign,
              currentDashaLord: currentDasha.isNotEmpty ? currentDasha.first.lord : null,
            ),
            const SizedBox(height: 16),
            _AnswerCard(answer: result.answer),
            const SizedBox(height: 24),
            Text('Planetary Positions', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            _PlanetsTable(planets: chart.planets),
            const SizedBox(height: 24),
            Text('Vimshottari Mahadasha', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            _DashaTimeline(periods: chart.mahadasha),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final String ascendantSign;
  final String moonSign;
  final String? currentDashaLord;

  const _SummaryCard({
    required this.ascendantSign,
    required this.moonSign,
    required this.currentDashaLord,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _SummaryItem(label: 'Ascendant', value: ascendantSign),
            _SummaryItem(label: 'Moon Sign', value: moonSign),
            _SummaryItem(label: 'Mahadasha', value: currentDashaLord ?? '—'),
          ],
        ),
      ),
    );
  }
}

class _SummaryItem extends StatelessWidget {
  final String label;
  final String value;

  const _SummaryItem({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value,
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _AnswerCard extends StatelessWidget {
  final String answer;

  const _AnswerCard({required this.answer});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: Theme.of(context).colorScheme.primary, size: 20),
                const SizedBox(width: 8),
                Text('Your Reading', style: Theme.of(context).textTheme.titleMedium),
              ],
            ),
            const SizedBox(height: 12),
            Text(answer, style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.5)),
          ],
        ),
      ),
    );
  }
}

class _PlanetsTable extends StatelessWidget {
  final List<PlanetPosition> planets;

  const _PlanetsTable({required this.planets});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: planets
            .map((p) => ListTile(
                  dense: true,
                  leading: CircleAvatar(
                    radius: 16,
                    child: Text(p.name.substring(0, 2)),
                  ),
                  title: Text(p.name),
                  subtitle: Text('${p.nakshatra} · pada ${p.pada}'),
                  trailing: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(p.sign, style: const TextStyle(fontWeight: FontWeight.w600)),
                      Text('House ${p.house}',
                          style: Theme.of(context).textTheme.bodySmall),
                    ],
                  ),
                ))
            .toList(),
      ),
    );
  }
}

class _DashaTimeline extends StatelessWidget {
  final List<DashaPeriod> periods;

  const _DashaTimeline({required this.periods});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: periods
            .map((d) => ListTile(
                  dense: true,
                  leading: Icon(
                    d.current ? Icons.radio_button_checked : Icons.circle_outlined,
                    color: d.current ? Theme.of(context).colorScheme.primary : Colors.grey,
                  ),
                  title: Text(
                    d.lord,
                    style: TextStyle(fontWeight: d.current ? FontWeight.bold : FontWeight.normal),
                  ),
                  trailing: Text('${d.start.toStringAsFixed(1)} – ${d.end.toStringAsFixed(1)}'),
                ))
            .toList(),
      ),
    );
  }
}
