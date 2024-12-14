const fs = require('fs');
const path = require('path');

/**
 * Рекурсивный парсинг зависимостей npm-пакета.
 * @param {string} packageDir - Путь к корню npm-пакета.
 * @param {number} maxDepth - Максимальная глубина анализа.
 * @returns {Object} Граф зависимостей.
 */
function parseDependencies(packageDir, maxDepth = 3) {
    const graph = {};

    function parseRecursive(packageName, currentDepth, visited) {
        if (currentDepth > maxDepth || visited.has(packageName)) return;

        visited.add(packageName);

        const packagePath = path.join(packageDir, 'node_modules', packageName, 'package.json');
        if (!fs.existsSync(packagePath)) return;

        const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf-8'));
        const dependencies = packageJson.dependencies || {};

        graph[packageName] = Object.keys(dependencies);

        for (const dep of Object.keys(dependencies)) {
            parseRecursive(dep, currentDepth + 1, visited);
        }
    }

    // Читаем корневой package.json
    const rootPackageJsonPath = path.join(packageDir, 'package.json');
    if (!fs.existsSync(rootPackageJsonPath)) {
        throw new Error('Файл package.json не найден.');
    }

    const rootPackageJson = JSON.parse(fs.readFileSync(rootPackageJsonPath, 'utf-8'));
    const rootDependencies = rootPackageJson.dependencies || {};

    graph[rootPackageJson.name] = Object.keys(rootDependencies);

    for (const dep of Object.keys(rootDependencies)) {
        parseRecursive(dep, 1, new Set());
    }

    return graph;
}

module.exports = parseDependencies;