// require.context do webpack (usado pelo Remotion) para registrar composições de projetos pessoais.
declare namespace NodeJS {
	interface Require {
		context(
			pasta: string,
			recursivo: boolean,
			filtro: RegExp,
		): {
			keys(): string[];
			<T = unknown>(id: string): T;
		};
	}
}
