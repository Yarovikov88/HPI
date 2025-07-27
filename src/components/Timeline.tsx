import React from 'react';
import type { CardNode, HpiMetric } from '../data/myWayNodes';
import styles from './Timeline.module.css';

// HPI Metrics sub-component
const HpiMetrics = ({ metrics }: { metrics: HpiMetric[] }) => (
  <div className={styles.hpiMetrics}>
    {metrics.map((metric, index) => (
      <div key={index} className={styles.hpiMetric}>
        <span className={styles.hpiSphere}>{metric.sphere}</span>
        <span className={styles.hpiValue}>{metric.value > 0 ? `+${metric.value}` : metric.value}</span>
      </div>
    ))}
  </div>
);

// A single timeline card
const TimelineCard = ({ node }: { node: CardNode }) => {
  return (
    <div className={styles.card}>
      <p className={styles.cardTitle}>{node.title}</p>
      <div className={styles.cardPeriod}>{node.period}</div>
      <div className={styles.cardHpiWrapper}>
        {node.hpi_metrics && <HpiMetrics metrics={node.hpi_metrics} />}
      </div>
    </div>
  );
};

const parsePeriod = (period: string): { start: number; end: number } => {
  const years = period.split('-').map((y) => parseInt(y.trim()));
  if (years.length === 2) {
    return { start: years[0], end: years[1] };
  }
  return { start: years[0], end: years[0] };
};

const groupNodesSmartly = (nodes: CardNode[]): Record<string, { workNodes: CardNode[]; lifeNodes: CardNode[] }> => {
  if (!nodes || nodes.length === 0) return {};

  const nodesWithYears = nodes
    .map((node) => ({ ...node, ...parsePeriod(node.period) }))
    .sort((a, b) => a.start - b.start || a.end - b.end);

  const finalGroups: Record<string, { workNodes: CardNode[]; lifeNodes: CardNode[] }> = {};

  nodesWithYears.forEach((node) => {
    let placed = false;
    const sortedGroupYears = Object.keys(finalGroups).sort((a, b) => parseInt(a) - parseInt(b));

    for (const year of sortedGroupYears) {
      const group = finalGroups[year];
      const oppositeNodes = node.type === 'work' ? group.lifeNodes : group.workNodes;

      const hasParent = oppositeNodes.some((p) => {
        const pYears = parsePeriod(p.period);
        return node.start >= pYears.start && node.start <= pYears.end;
      });

      if (hasParent) {
        if (node.type === 'work') {
          group.workNodes.push(node);
        } else {
          group.lifeNodes.push(node);
        }
        placed = true;
        break;
      }
    }

    if (!placed) {
      const startYearStr = String(node.start);
      if (!finalGroups[startYearStr]) {
        finalGroups[startYearStr] = { workNodes: [], lifeNodes: [] };
      }
      if (node.type === 'work') {
        finalGroups[startYearStr].workNodes.push(node);
      } else {
        finalGroups[startYearStr].lifeNodes.push(node);
      }
    }
  });

  return finalGroups;
};

const pairNodes = (
  workNodes: CardNode[],
  lifeNodes: CardNode[]
): { workNode?: CardNode; lifeNode?: CardNode }[] => {
  const unpairedWork = [...workNodes];
  const unpairedLife = [...lifeNodes];
  const pairs: { workNode?: CardNode; lifeNode?: CardNode }[] = [];

  unpairedWork.forEach((work, i) => {
    let bestMatch: CardNode | null = null;
    let bestMatchIndex = -1;
    let smallestDiff = Infinity;

    const workYears = parsePeriod(work.period);

    unpairedLife.forEach((life, j) => {
      const lifeYears = parsePeriod(life.period);
      const overlaps = workYears.start <= lifeYears.end && workYears.end >= lifeYears.start;

      if (overlaps) {
        const diff = Math.abs(workYears.start - lifeYears.start);
        if (diff < smallestDiff) {
          smallestDiff = diff;
          bestMatch = life;
          bestMatchIndex = j;
        }
      }
    });

    if (bestMatch && bestMatchIndex !== -1) {
      pairs.push({ workNode: work, lifeNode: bestMatch });
      unpairedLife.splice(bestMatchIndex, 1);
    } else {
      pairs.push({ workNode: work, lifeNode: undefined });
    }
  });

  unpairedLife.forEach((life) => {
    pairs.push({ workNode: undefined, lifeNode: life });
  });
  
  return pairs.sort((a,b) => {
    const yearA = a.workNode ? parsePeriod(a.workNode.period).start : parsePeriod(a.lifeNode!.period).start;
    const yearB = b.workNode ? parsePeriod(b.workNode.period).start : parsePeriod(b.lifeNode!.period).start;
    return yearA - yearB;
  });
};

// The Timeline component that renders a list of cards
const Timeline = ({ nodes }: { nodes: CardNode[] }) => {
  const groupedNodes = groupNodesSmartly(nodes);
  const sortedYears = Object.keys(groupedNodes).sort(
    (a, b) => parseInt(a) - parseInt(b)
  );

  return (
    <div className={styles.timelineContainer}>
      {sortedYears.map((year) => {
        const { workNodes, lifeNodes } = groupedNodes[year];
        const pairedRows = pairNodes(workNodes, lifeNodes);

        return (
          <div key={year} className={styles.yearSection}>
            {/* <div className={styles.yearMarker}>{year}</div> */}
            {pairedRows.map(({ workNode, lifeNode }, i) => (
              <TimelineRow key={i} workNode={workNode} lifeNode={lifeNode} />
            ))}
                      </div>
        );
      })}
                      </div>
  );
};

const TimelineRow = ({ workNode, lifeNode }: { workNode?: CardNode, lifeNode?: CardNode }) => {
  return (
    <div className={styles.timelineRow}>
      <div className={styles.leftCell}>
        {workNode && <TimelineCard node={workNode} />}
                    </div>
      <div className={styles.centerCell} />
      <div className={styles.rightCell}>
        {lifeNode && <TimelineCard node={lifeNode} />}
              </div>
    </div>
  );
};

export default Timeline; 