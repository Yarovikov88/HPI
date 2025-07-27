import { Outlet } from 'react-router-dom';

export default function FeaturesPage() {
  return (
    <div>
      <h1>Возможности HPI.EXPERT</h1>
      <p>
        Узнайте подробнее о ключевых инструментах нашей платформы, которые помогут вам в системном развитии.
      </p>
      <hr />
      <Outlet />
    </div>
  );
} 