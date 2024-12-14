import { expect } from 'chai';
import fs from 'fs';
import mockFs from 'mock-fs';
import parseDependencies from './package-parser.js';
import { generatePlantUML } from './plantuml-gen.js';


describe('Dependency Visualizer', () => {
    afterEach(() => {
        mockFs.restore(); // Восстановление файловой системы после каждого теста
    });

    describe('parseDependencies', () => {
        it('должен корректно парсить зависимости', () => {
            // Мока файловой системы
            mockFs({
                'node_modules': {
                    'pkg1': {
                        'package.json': JSON.stringify({
                            name: 'pkg1',
                            dependencies: {
                                'pkg2': '1.0.0',
                            },
                        }),
                    },
                    'pkg2': {
                        'package.json': JSON.stringify({
                            name: 'pkg2',
                        }),
                    },
                },
            });

            const result = parseDependencies('node_modules/pkg1', 2);
            expect(result).to.deep.equal({
                name: 'pkg1',
                dependencies: [
                    {
                        name: 'pkg2',
                        dependencies: [],
                    },
                ],
            });
        });
    });

    describe('generatePlantUML', () => {
        it('должен корректно генерировать PlantUML код', () => {
            const graph = {
                name: 'pkg1',
                dependencies: [
                    {
                        name: 'pkg2',
                        dependencies: [],
                    },
                ],
            };
            const plantUML = generatePlantUML(graph);
            expect(plantUML).to.contain('pkg1 --> pkg2');
        });
    });
});
