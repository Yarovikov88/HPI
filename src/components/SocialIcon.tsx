import React from 'react';

type IconProps = {
  name: 'tg' | 'linkedin' | 'email';
  size?: number;
  color?: string;
};

const iconPaths = {
  tg: "M22.7,1.8l-3.9,18.1c-0.2,1.1-0.8,1.4-1.7,0.9l-5.7-4.2l-2.8,2.7c-0.3,0.3-0.6,0.6-1.1,0.6l0.4-5.8l10.8-9.6c0.5-0.4-0.1-0.7-0.7-0.3L7.3,13.4l-5.5-1.7c-1.1-0.3-1.1-1.2,0.2-1.8L21.2,0.3C22.2,0,23,0.6,22.7,1.8z",
  linkedin: "M20.5,0h-17C1.6,0,0,1.6,0,3.5v17C0,22.4,1.6,24,3.5,24h17c1.9,0,3.5-1.6,3.5-3.5v-17C24,1.6,22.4,0,20.5,0z M8,19H5V8h3V19z M6.5,6.7c-1,0-1.8-0.8-1.8-1.8s0.8-1.8,1.8-1.8s1.8,0.8,1.8,1.8S7.5,6.7,6.5,6.7z M19,19h-3v-5.4c0-1.3-0-3-1.8-3s-2.1,1.4-2.1,2.9V19H9V8h3v1.4h0c0.4-0.8,1.5-1.6,3-1.6c3.2,0,3.8,2.1,3.8,4.8V19z",
  email: "M22,5.2H2C1.5,5.2,1,5.7,1,6.2v11.5C1,18.4,1.5,19,2,19h20c0.5,0,1-0.6,1-1.2V6.2C23,5.7,22.5,5.2,22,5.2z M21.2,7L12,13.6L2.8,7H21.2z M2,17.8V8.1l9.9,7.2c0.1,0.1,0.2,0.1,0.3,0.1s0.2,0,0.3-0.1l9.9-7.2v9.7H2z"
};

const SocialIcon: React.FC<IconProps> = ({ name, size = 24, color = 'currentColor' }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ color }}
    >
      <path d={iconPaths[name]} fill="currentColor" />
    </svg>
  );
};

export default SocialIcon; 