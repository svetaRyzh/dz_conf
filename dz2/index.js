const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const parseDependencies = require('./package-parser');
const generatePlantUML = require('./plantuml-gen');

// Чтение аргументов командной строки
const args = require('yargs')
    .option('path', {
        alias: 'p',
        describe: 'Путь к программе PlantUML.',
        demandOption: true,
        type: 'string',
    })
    .option('package', {
        alias: 'pkg',
        describe: 'Путь к корневому каталогу npm-пакета.',
        demandOption: true,
        type: 'string',
    })
    .option('depth', {
        alias: 'd',
        describe: 'Максимальная глубина анализа зависимостей.',
        default: 3,
        type: 'number',
    })
    .help()
    .argv;

// Основная логика
(async () => {
    try {
        // Парсинг зависимостей
        const graph = parseDependencies(args.package, args.depth);

        // Генерация PlantUML
        const plantUMLCode = generatePlantUML(graph);
        const umlFilePath = path.resolve('graph.puml');
        fs.writeFileSync(umlFilePath, plantUMLCode);

        // Вызов программы PlantUML
        exec(`java -jar ${args.path} ${umlFilePath}`, (err, stdout, stderr) => {
            if (err) {
                console.error('Ошибка при вызове PlantUML:', stderr);
                process.exit(1);
            }
            console.log('Диаграмма успешно сгенерирована.');
            console.log(stdout);
        });
    } catch (error) {
        console.error('Произошла ошибка:', error.message);
        process.exit(1);
    }
})();
