/**
 * Генерация PlantUML-диаграммы из графа зависимостей.
 * @param {Object} graph - Граф зависимостей.
 * @returns {string} Описание диаграммы PlantUML.
 */
function generatePlantUML(graph) {
    const lines = ['@startuml', 'digraph G {'];

    for (const [node, dependencies] of Object.entries(graph)) {
        for (const dep of dependencies) {
            lines.push(`  "${node}" -> "${dep}";`);
        }
    }

    lines.push('}', '@enduml');
    return lines.join('\n');
}

module.exports = generatePlantUML;