
import React, { useEffect, useState, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Calendar from 'react-calendar';
// import 'react-calendar/dist/Calendar.css'; // ПОЛНОСТЬЮ ОТКЛЮЧАЕМ СТИЛИ БИБЛИОТЕКИ
import styles from "./CalendarWidget.module.css";
import { format, parseISO } from "date-fns";
import { apiClient, type CalendarDayStatus } from "../services/api";

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];

export function CalendarWidget() {
    const navigate = useNavigate();
    const location = useLocation();
    const [monthStatuses, setMonthStatuses] = useState<Record<string, CalendarDayStatus>>({});
    const [value, setValue] = useState<Value>(() => {
        const params = new URLSearchParams(location.search);
        const dateStr = params.get("date");
        return dateStr ? parseISO(dateStr) : null;
    });

    const [activeStartDate, setActiveStartDate] = useState<Date>(() => {
        const initial = value && value instanceof Date ? value : new Date();
        return new Date(initial.getFullYear(), initial.getMonth(), 1);
    });

    // Загружаем статусы для видимого месяца
    useEffect(() => {
        const fetchStatuses = async () => {
            try {
                const from = format(activeStartDate, 'yyyy-MM-01');
                const toDate = new Date(activeStartDate.getFullYear(), activeStartDate.getMonth() + 1, 0);
                const to = format(toDate, 'yyyy-MM-dd');
                const data = await apiClient.getCalendarStatus(from, to);
                const map: Record<string, CalendarDayStatus> = {};
                (data || []).forEach((d) => { map[d.date] = d; });
                setMonthStatuses(map);
            } catch (e) {
                console.error('Failed to load calendar statuses:', e);
                setMonthStatuses({});
            }
        };
        fetchStatuses();
    }, [activeStartDate]);
    
    const handleDayClick = (newValue: Value) => {
        setValue(newValue);
        const params = new URLSearchParams(location.search);
        if (newValue && newValue instanceof Date) {
            params.set("date", format(newValue, "yyyy-MM-dd"));
        } else {
            params.delete("date");
        }
        navigate({ pathname: '/account/diagnostics', search: params.toString() });
    };

    const tileClassName = ({ date, view }: { date: Date, view: string }) => {
        if (view === 'month') {
            const classNames: string[] = [];
            const dateString = format(date, 'yyyy-MM-dd');
            const todayString = format(new Date(), 'yyyy-MM-dd');
            const status = monthStatuses[dateString];

            // Полностью завершено (basic.complete и pro.complete) -> синий
            if (status && status.basic?.status === 'complete' && status.pro?.status === 'complete') {
                classNames.push(styles.completed);
            } else if (status && (status.basic?.status === 'draft' || status.pro?.status === 'draft' || status.basic?.status === 'complete' || status.pro?.status === 'complete')) {
                // Любая активность, но не полное завершение обеих -> коричневый
                classNames.push(styles.draft);
            }

            // Текущая дата — красная обводка поверх
            if (dateString === todayString) {
                classNames.push(styles.todayOutline);
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
                onActiveStartDateChange={({ activeStartDate }) => {
                    if (activeStartDate) setActiveStartDate(activeStartDate);
                }}
                navigationLabel={({ date, label, locale, view }) => label.replace(' г.', '')}
            />
        </div>
    );
} 