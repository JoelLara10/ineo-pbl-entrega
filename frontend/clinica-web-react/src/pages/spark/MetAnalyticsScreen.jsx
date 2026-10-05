import SparkAnalysisScreen from './SparkAnalysisScreen';
import MetOperationalPanel from './MetOperationalPanel';

export default function MetAnalyticsScreen() {
  return <SparkAnalysisScreen type="met" ResultsComponent={MetOperationalPanel} />;
}
