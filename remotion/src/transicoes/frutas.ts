// Frutas chapadas em SVG (data URI) para a chuva de objetos. Troque as cores pela paleta da marca
// ou passe suas próprias imagens (staticFile('objetos/x.png')) para ChuvaDeObjetos.

export type CoresFrutas = {vermelho: string; verde: string; laranja: string; amarelo: string; uva: string; folha: string; brilho: string};

export const CORES_PADRAO: CoresFrutas = {
	vermelho: '#FF5A3C',
	verde: '#7BD13A',
	laranja: '#CA8A3B',
	amarelo: '#E3B341',
	uva: '#3F7F2E',
	folha: '#2E6B2A',
	brilho: 'rgba(255,255,255,0.45)',
};

const uri = (svg: string) => `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;

export const frutasSvg = (c: CoresFrutas = CORES_PADRAO): string[] => [
	uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle fill="${c.vermelho}" cx="50" cy="56" r="38"/><ellipse fill="${c.brilho}" cx="35" cy="42" rx="9" ry="6" transform="rotate(-30 35 42)"/><path fill="${c.folha}" d="M50 22 L58 11 L57 24 L71 21 L60 30 L50 27 L40 30 L29 21 L43 24 L42 11 Z"/></svg>`),
	uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle fill="${c.laranja}" cx="50" cy="55" r="38"/><ellipse fill="${c.brilho}" cx="35" cy="41" rx="9" ry="6" transform="rotate(-30 35 41)"/><path fill="${c.folha}" d="M50 18 Q66 2 82 13 Q66 26 50 18 Z"/></svg>`),
	uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="${c.verde}" d="M6 50 Q50 8 94 50 Q50 92 6 50 Z"/><ellipse fill="${c.brilho}" cx="38" cy="39" rx="11" ry="4" transform="rotate(-15 38 39)"/></svg>`),
	uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="${c.amarelo}" d="M14 26 Q22 86 86 76 Q92 70 85 65 Q36 66 27 22 Z"/><path fill="${c.folha}" d="M10 17 L27 22 L22 31 Z"/></svg>`),
	uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g fill="${c.uva}"><circle cx="36" cy="36" r="13"/><circle cx="62" cy="36" r="13"/><circle cx="49" cy="57" r="13"/><circle cx="24" cy="57" r="11"/><circle cx="74" cy="57" r="11"/><circle cx="49" cy="80" r="12"/></g><path fill="${c.folha}" d="M48 22 Q60 3 80 11 Q64 23 48 22 Z"/></svg>`),
];
