import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Dimensions,
  RefreshControl,
} from 'react-native';
import {
  Text,
  SegmentedButtons,
  Card,
  ActivityIndicator,
} from 'react-native-paper';
import { LineChart, BarChart } from 'react-native-chart-kit';
import { colors, spacing, fontSizes } from '../../theme/colors';
import { statisticsService } from '../../services/api/statisticsService';
import type { StatisticsResponse } from '../../services/api/statisticsService';

const screenWidth = Dimensions.get('window').width;

const chartConfig = {
  backgroundColor: colors.primary,
  backgroundGradientFrom: colors.primary,
  backgroundGradientTo: colors.primary,
  decimalPlaces: 1,
  color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
  labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
  style: {
    borderRadius: 16,
  },
  propsForDots: {
    r: '4',
    strokeWidth: '2',
    stroke: colors.primary,
  },
};

export default function StatisticsScreen() {
  const [period, setPeriod] = useState('week');
  const [stats, setStats] = useState<StatisticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadStatistics = async () => {
    try {
      setIsLoading(true);
      let data: StatisticsResponse;

      if (period === 'week') {
        data = await statisticsService.getWeeklyStatistics();
      } else {
        data = await statisticsService.getMonthlyStatistics();
      }

      setStats(data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadStatistics();
  }, [period]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    loadStatistics();
  };

  // Prepare chart data
  const prepareChartData = (data: Array<{ date: string; value: number }>) => {
    if (!data || data.length === 0) {
      return {
        labels: ['No data'],
        datasets: [{ data: [0] }],
      };
    }

    // Take last 7 or 30 data points
    const maxPoints = period === 'week' ? 7 : 30;
    const sliced = data.slice(-maxPoints);

    return {
      labels: sliced.map((item) => {
        const date = new Date(item.date);
        return `${date.getDate()}/${date.getMonth() + 1}`;
      }),
      datasets: [
        {
          data: sliced.map((item) => item.value || 0),
        },
      ],
    };
  };

  if (isLoading && !stats) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading statistics...</Text>
      </View>
    );
  }

  const weightData = stats?.weight ? prepareChartData(stats.weight) : null;
  const caloriesData = stats?.calories
    ? prepareChartData(stats.calories)
    : null;
  const waterData = stats?.water ? prepareChartData(stats.water) : null;
  const sleepData = stats?.sleep ? prepareChartData(stats.sleep) : null;
  const exerciseData = stats?.exercise
    ? prepareChartData(stats.exercise)
    : null;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.content}>
        {/* Header */}
        <Text style={styles.title}>Statistics</Text>
        <Text style={styles.subtitle}>Track your progress over time</Text>

        {/* Period Selector */}
        <SegmentedButtons
          value={period}
          onValueChange={setPeriod}
          buttons={[
            { value: 'week', label: 'Week' },
            { value: 'month', label: 'Month' },
          ]}
          style={styles.periodSelector}
        />

        {/* Weight Chart */}
        {weightData && weightData.datasets[0].data.some((v) => v > 0) && (
          <Card style={styles.chartCard}>
            <Card.Title title="Weight Trend" titleVariant="titleMedium" />
            <Card.Content>
              <LineChart
                data={weightData}
                width={screenWidth - spacing.lg * 4}
                height={220}
                chartConfig={chartConfig}
                bezier
                style={styles.chart}
                withVerticalLabels={true}
                withHorizontalLabels={true}
                withDots={true}
                withInnerLines={true}
                withOuterLines={true}
              />
            </Card.Content>
          </Card>
        )}

        {/* Calories Chart */}
        {caloriesData && caloriesData.datasets[0].data.some((v) => v > 0) && (
          <Card style={styles.chartCard}>
            <Card.Title title="Calories Consumed" titleVariant="titleMedium" />
            <Card.Content>
              <BarChart
                data={caloriesData}
                width={screenWidth - spacing.lg * 4}
                height={220}
                chartConfig={chartConfig}
                style={styles.chart}
                yAxisSuffix=" kcal"
                fromZero
              />
            </Card.Content>
          </Card>
        )}

        {/* Water Intake Chart */}
        {waterData && waterData.datasets[0].data.some((v) => v > 0) && (
          <Card style={styles.chartCard}>
            <Card.Title title="Water Intake" titleVariant="titleMedium" />
            <Card.Content>
              <BarChart
                data={waterData}
                width={screenWidth - spacing.lg * 4}
                height={220}
                chartConfig={chartConfig}
                style={styles.chart}
                yAxisSuffix=" ml"
                fromZero
              />
            </Card.Content>
          </Card>
        )}

        {/* Sleep Chart */}
        {sleepData && sleepData.datasets[0].data.some((v) => v > 0) && (
          <Card style={styles.chartCard}>
            <Card.Title title="Sleep Duration" titleVariant="titleMedium" />
            <Card.Content>
              <LineChart
                data={sleepData}
                width={screenWidth - spacing.lg * 4}
                height={220}
                chartConfig={chartConfig}
                bezier
                style={styles.chart}
                yAxisSuffix=" hrs"
              />
            </Card.Content>
          </Card>
        )}

        {/* Exercise Chart */}
        {exerciseData && exerciseData.datasets[0].data.some((v) => v > 0) && (
          <Card style={styles.chartCard}>
            <Card.Title
              title="Exercise Duration"
              titleVariant="titleMedium"
            />
            <Card.Content>
              <BarChart
                data={exerciseData}
                width={screenWidth - spacing.lg * 4}
                height={220}
                chartConfig={chartConfig}
                style={styles.chart}
                yAxisSuffix=" min"
                fromZero
              />
            </Card.Content>
          </Card>
        )}

        {/* Empty State */}
        {stats &&
          !weightData?.datasets[0].data.some((v) => v > 0) &&
          !caloriesData?.datasets[0].data.some((v) => v > 0) && (
            <Card style={styles.emptyCard}>
              <Card.Content>
                <Text style={styles.emptyText}>
                  No data available for the selected period. Start tracking your
                  health to see statistics here!
                </Text>
              </Card.Content>
            </Card>
          )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  content: {
    padding: spacing.lg,
  },
  title: {
    fontSize: fontSizes.xxl,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    marginBottom: spacing.lg,
  },
  periodSelector: {
    marginBottom: spacing.xl,
  },
  chartCard: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  chart: {
    marginVertical: spacing.md,
    borderRadius: 16,
  },
  emptyCard: {
    padding: spacing.xl,
    backgroundColor: colors.backgroundSecondary,
  },
  emptyText: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});
