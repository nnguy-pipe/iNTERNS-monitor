const severityOrder = {
  Critical: 1,
  High: 2,
  Medium: 3,
  Low: 4,
};

export function sortAlertsBySeverity(alerts) {
  return [...alerts].sort((a, b) => {
    const priorityA = severityOrder[a.severity] || 99;
    const priorityB = severityOrder[b.severity] || 99;
    return priorityA - priorityB;
  });
}
