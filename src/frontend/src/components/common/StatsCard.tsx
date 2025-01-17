import React, { ReactNode } from 'react';
import { IconType } from 'react-icons';

interface StatsCardProps {
  icon: ReactNode;
  value: string | number;
  label: string;
  color?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({
  icon,
  value,
  label,
  color = 'primary'
}) => {
  return (
    <div className={`stats-card bg-${color}`}>
      <div className="d-flex justify-content-between align-items-center">
        <div>
          <div className="stats-value">{value}</div>
          <div className="stats-label">{label}</div>
        </div>
        <div className="stats-icon">{icon}</div>
      </div>
    </div>
  );
};

export default StatsCard;
