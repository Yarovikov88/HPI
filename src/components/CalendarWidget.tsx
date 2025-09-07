
import React, { useEffect, useState, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css'; // включаем базовые стили библиотеки для корректной сетки
import styles from "./CalendarWidget.module.css";
import { format } from "date-fns";
import { apiClient, type CalendarDayStatus } from "../services/api";
import { useSurvey } from "../hooks/useSurvey";

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];

function parseYmdToLocalNoon(ymd: string | null): Date | null {
    if (!ymd) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd);
    if (!m) return null;
    const y = Number(m[1]);
    const mm = Number(m[2]);
    const dd = Number(m[3]);
    return new Date(y, mm - 1, dd, 12, 0, 0, 0); // локальный полдень, чтобы исключить смещения по TZ/DST
}

export function CalendarWidget() {
    const navigate = useNavigate();
    const location = useLocation();
    const { setSelectedDate, selectedDate, proCompletionStatus } = useSurvey();
    const [monthStatuses, setMonthStatuses] = useState<Record<string, CalendarDayStatus>>({});
    const [value, setValue] = useState<Value>(() => {
        const params = new URLSearchParams(location.search);
        const dateStr = params.get("date");
        return parseYmdToLocalNoon(dateStr);
    });

    const [activeStartDate, setActiveStartDate] = useState<Date>(() => {
        const initial = value && value instanceof Date ? value : new Date();
        return new Date(initial.getFullYear(), initial.getMonth(), 1);
    });

    // Принудительная инициализация при заходе на страницу: синхронизируем глобальную дату и URL
    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const dateStr = params.get('date');
        const initDate = parseYmdToLocalNoon(dateStr) || new Date();

        // 1) Ставим дату в контекст (для остальных страниц)
        setSelectedDate(initDate);
        // 2) Синхронизируем локальное состояние календаря
        setValue(initDate);
        setActiveStartDate(new Date(initDate.getFullYear(), initDate.getMonth(), 1));
        // 3) Если в URL нет даты — добавим сегодняшнюю
        if (!dateStr) {
            const ds = format(initDate, 'yyyy-MM-dd');
            params.set('date', ds);
            navigate(`${location.pathname}?${params.toString()}`, { replace: true });
        }
    }, []);

    // Синхронизация выделенной даты при изменении URL (?date=)
    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const dateStr = params.get('date');
        const next = parseYmdToLocalNoon(dateStr);
        setValue(next);
        if (next instanceof Date && !Number.isNaN(next.getTime())) {
            setActiveStartDate(new Date(next.getFullYear(), next.getMonth(), 1));
        }
    }, [location.search]);

    // Загружаем/перезагружаем статусы для видимого месяца
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
    }, [activeStartDate, proCompletionStatus, selectedDate]);
    
    const handleDayClick = (newValue: Value) => {
        if (newValue instanceof Date) {
            // 1. Update the global state first
            setSelectedDate(newValue);

            // 2. Update the local state for the calendar UI
            setValue(newValue);

            // 3. Update the URL of the CURRENT page (preserve path and other params)
            const dateString = format(newValue, "yyyy-MM-dd");
            const params = new URLSearchParams(location.search);
            params.set('date', dateString);
            navigate(`${location.pathname}?${params.toString()}`, { replace: true });
        }
    };

    const tileClassName = ({ date, view }: { date: Date, view: string }) => {
        if (view === 'month') {
            const classNames: string[] = [];
            const dateString = format(date, 'yyyy-MM-dd');
            const todayString = format(new Date(), 'yyyy-MM-dd');
            const status = monthStatuses[dateString];

            const isBasicComplete = status?.basic?.status === 'complete' || (!!status?.basic?.total && status.basic.answered === status.basic.total);
            const isProComplete = status?.pro?.status === 'complete' || (!!status?.pro?.total && status.pro.answered === status.pro.total);

            // Полностью завершено (basic и pro) -> синий
            if (isBasicComplete && isProComplete) {
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
                calendarType="iso8601" /* неделя начинается с понедельника */
                tileClassName={tileClassName}
                className={styles.reactCalendar}
                onActiveStartDateChange={({ activeStartDate }) => {
                    if (activeStartDate) setActiveStartDate(activeStartDate);
                }}
                navigationLabel={({ date, label }) => label.replace(' г.', '')}
                showNeighboringMonth={false}
            />
        </div>
    );
} 