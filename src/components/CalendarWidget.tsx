
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Calendar from 'react-calendar';
// import 'react-calendar/dist/Calendar.css'; // ПОЛНОСТЬЮ ОТКЛЮЧАЕМ СТИЛИ БИБЛИОТЕКИ
import styles from "./CalendarWidget.module.css";
// import { apiClient } from "../services/api"; // ВРЕМЕННО ОТКЛЮЧЕНО
import { format, parseISO } from "date-fns";

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];

export function CalendarWidget() {
    const navigate = useNavigate();
    const location = useLocation();
    const [completedDates, setCompletedDates] = useState<string[]>([]);
    const [value, setValue] = useState<Value>(() => {
        const params = new URLSearchParams(location.search);
        const dateStr = params.get("date");
        return dateStr ? parseISO(dateStr) : null;
    });

    useEffect(() => {
        // apiClient.getCompletedDates()
        //     .then(dates => {
        //         setCompletedDates(dates); // Даты приходят как строки 'YYYY-MM-DD'
        //     })
        //     .catch(error => {
        //         console.error("Failed to fetch diagnostic dates:", error);
        //     });
        console.warn('Fetching completed dates is disabled in CalendarWidget.');
    }, []);
    
    const handleDayClick = (newValue: Value) => {
        setValue(newValue);
        const params = new URLSearchParams(location.search);
        if (newValue && newValue instanceof Date) {
            params.set("date", format(newValue, "yyyy-MM-dd"));
        } else {
            params.delete("date");
        }
        navigate({ search: params.toString() });
    };

    const tileClassName = ({ date, view }: { date: Date, view: string }) => {
        if (view === 'month') {
            const classNames = [];
            const dateString = format(date, 'yyyy-MM-dd');
            const todayString = format(new Date(), 'yyyy-MM-dd');

            // Сначала добавляем базовый стиль для пройденных
            if (completedDates.includes(dateString)) {
                classNames.push(styles.completed);
            }
            // Затем добавляем стиль для сегодняшней даты, он будет иметь приоритет
            if (dateString === todayString) {
                classNames.push(styles.today);
            }
    
            return classNames.length > 0 ? classNames.join(' ') : null;
        }
        return null;
    };

    return (
        <div className={styles.calendarContainer}>
            <Calendar
                onChange={handleDayClick}
                value={value}
                locale="ru-RU"
                tileClassName={tileClassName}
                className={styles.reactCalendar}
                navigationLabel={({ date, label, locale, view }) => label.replace(' г.', '')}
            />
        </div>
    );
} 