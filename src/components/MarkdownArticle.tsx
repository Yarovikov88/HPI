import React from 'react';

type MarkdownArticleProps = {
	content: string;
	className?: string;
};

type Section = {
	title?: string;
	children: React.ReactNode[];
};

// Lightweight markdown renderer with section cards per H2
export const MarkdownArticle: React.FC<MarkdownArticleProps> = ({ content, className }) => {
	const lines = content.replaceAll('\r\n', '\n').split('\n');
	const elements: React.ReactNode[] = [];
	const sections: Section[] = [];
	let current: Section | null = null;
	let topTitle: string | null = null;
	let listBuffer: string[] = [];

	const flushList = () => {
		if (listBuffer.length > 0) {
			(current?.children || elements).push(
				<ul key={`ul-${(current?.children.length ?? elements.length)}-${Math.random()}`}>
					{listBuffer.map((item, idx) => (
						<li key={idx}>{item}</li>
					))}
				</ul>
			);
			listBuffer = [];
		}
	};

	const startSection = (title?: string) => {
		if (current) sections.push(current);
		current = { title, children: [] };
	};

	lines.forEach((raw, idx) => {
		const line = raw.trimEnd();
		if (line.trim() === '') { flushList(); return; }
		const h1 = line.match(/^#\s+(.*)$/);
		if (h1) { flushList(); topTitle = h1[1]; return; }
		const h2 = line.match(/^##\s+(.*)$/);
		if (h2) { flushList(); startSection(h2[1]); return; }
		const h3 = line.match(/^###\s+(.*)$/);
		if (h3) { flushList(); (current?.children || elements).push(<h3 key={`h3-${idx}`}>{h3[1]}</h3>); return; }
		const li = line.match(/^-\s+(.*)$/);
		if (li) { listBuffer.push(li[1]); return; }
		flushList();
		(current?.children || elements).push(<p key={`p-${idx}`}>{line}</p>);
	});
	flushList();
	if (current) sections.push(current);

	if (topTitle) {
		elements.unshift(<h1 key="top-title">{topTitle}</h1>);
	}

	sections.forEach((s, i) => {
		elements.push(
			<div key={`sec-${i}`} className="sectionCard">
				{ s.title ? <h2 className="sectionTitle">{s.title}</h2> : null }
				{ s.children }
			</div>
		);
	});

	return <article className={className}>{elements}</article>;
};

export default MarkdownArticle; 