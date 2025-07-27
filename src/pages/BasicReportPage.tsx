import { useSearchParams } from "react-router-dom";

const BasicReportPage = () => {
  const [searchParams] = useSearchParams();
  const date = searchParams.get("date");

  return (
    <div>
      <h1>Отчет по базовой диагностике</h1>
      <p>Дата: {date ? new Date(date).toLocaleDateString("ru-RU") : "Не указана"}</p>
      <p>Здесь будет отображаться отчет.</p>
    </div>
  );
};

export default BasicReportPage; 