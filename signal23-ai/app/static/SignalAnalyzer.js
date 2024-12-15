(function() {
    const { BarChart, Bar, XAxis, YAxis, ResponsiveContainer } = Recharts;

    // Data Panel Component
    const DataPanel = ({ title, children }) => {
        return React.createElement('div', {
            className: 'border border-[#00ffd9] bg-[#000810]/90 p-4 relative'
        }, [
            React.createElement('div', {
                key: 'border',
                className: 'absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#00ffd9]/0 via-[#00ffd9] to-[#00ffd9]/0 animate-pulse'
            }),
            React.createElement('div', {
                key: 'title',
                className: 'text-[#00ffd9] font-mono text-lg mb-4 uppercase'
            }, title),
            children
        ]);
    };

    // Signal Analyzer Component
    const SignalAnalyzer = () => {
        const [signalData, setSignalData] = React.useState([]);
        const [timestamp, setTimestamp] = React.useState('');

        React.useEffect(() => {
            const updateData = () => {
                const newData = Array.from({ length: 10 }, (_, i) => ({
                    time: i,
                    amplitude: Math.random() * 50 + 25,
                    frequency: Math.random() * 30 + 15
                }));
                setSignalData(newData);

                const now = new Date();
                const formatted = now.toISOString()
                    .replace('T', '')
                    .replace(/\..+/, '')
                    .replace(/-/g, '')
                    .replace(/:/g, '');
                setTimestamp(formatted + '.828Z');
            };

            updateData();
            const interval = setInterval(updateData, 2000);
            return () => clearInterval(interval);
        }, []);

        return React.createElement('div', {
            className: 'grid grid-cols-1 gap-4'
        }, [
            // Signal Analysis Panel
            React.createElement(DataPanel, {
                key: 'signal',
                title: 'SIGNAL ANALYSIS'
            }, React.createElement('div', {
                className: 'text-[#00ffd9] font-mono space-y-2'
            }, [
                React.createElement('div', { key: 'freq' }, 'FREQUENCY: 23.976 kHz'),
                React.createElement('div', { key: 'amp' }, 'AMPLITUDE: 47.223 dB'),
                React.createElement('div', { key: 'pattern' }, 'PATTERN: █░█░█░█░'),
                React.createElement('div', { 
                    key: 'analyzing',
                    className: 'animate-pulse'
                }, 'ANALYZING...')
            ])),

            // Temporal Data Panel
            React.createElement(DataPanel, {
                key: 'temporal',
                title: 'TEMPORAL DATA'
            }, React.createElement('div', {
                className: 'text-[#00ffd9] font-mono space-y-2'
            }, [
                React.createElement('div', { key: 'time' }, `TIME STAMP: ${timestamp}`),
                React.createElement('div', { key: 'drift' }, 'TEMPORAL DRIFT: 0.0023'),
                React.createElement('div', { key: 'variance' }, 'QUANTUM VARIANCE: 1.618'),
                React.createElement('div', { 
                    key: 'monitoring',
                    className: 'animate-pulse'
                }, 'MONITORING...')
            ])),

            // Frequency Map Panel with Chart
            React.createElement(DataPanel, {
                key: 'frequency',
                title: 'FREQUENCY MAP'
            }, React.createElement(ResponsiveContainer, {
                width: '100%',
                height: 150
            }, React.createElement(BarChart, {
                data: signalData,
                margin: { top: 5, right: 5, bottom: 5, left: 5 }
            }, [
                React.createElement(XAxis, {
                    key: 'x',
                    dataKey: 'time',
                    stroke: '#00ffd9'
                }),
                React.createElement(YAxis, {
                    key: 'y',
                    stroke: '#00ffd9'
                }),
                React.createElement(Bar, {
                    key: 'bar',
                    dataKey: 'frequency',
                    fill: '#00ffd9',
                    opacity: 0.8
                })
            ])))
        ]);
    };

    // Mount the component
    document.addEventListener('DOMContentLoaded', () => {
        const root = ReactDOM.createRoot(document.getElementById('signal-analyzer-root'));
        root.render(React.createElement(SignalAnalyzer));
    });
})();