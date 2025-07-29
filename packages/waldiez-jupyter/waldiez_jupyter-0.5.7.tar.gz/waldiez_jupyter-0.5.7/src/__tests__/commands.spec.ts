/**
 * SPDX-License-Identifier: Apache-2.0
 * Copyright 2024 - 2025 Waldiez & contributors
 */
import { CommandIDs, handleWaldiezCommands } from "../commands";
import { WaldiezEditor } from "../editor";
import { WaldiezEditorFactory } from "../factory";
import { mockFetch, patchServerConnection } from "./utils";
import { JupyterFrontEnd, JupyterLab } from "@jupyterlab/application";
import { WidgetTracker } from "@jupyterlab/apputils";
import { IFileBrowserFactory } from "@jupyterlab/filebrowser";
import { IMainMenu, MainMenu } from "@jupyterlab/mainmenu";

describe("Waldiez Commands", () => {
    let app: JupyterFrontEnd;
    let tracker: WidgetTracker<WaldiezEditor>;
    let fileBrowserFactory: IFileBrowserFactory;
    let widgetFactory: WaldiezEditorFactory;
    let mainMenu: IMainMenu;

    beforeEach(() => {
        mockFetch('{"composite": true}', false);
        patchServerConnection('{"composite": true}', false);
        app = new JupyterLab() as jest.Mocked<JupyterLab>;
        tracker = {} as WidgetTracker<WaldiezEditor>;
        fileBrowserFactory = {
            tracker: {
                currentWidget: {
                    model: {
                        path: "path/to/file.waldiez",
                        refresh: jest.fn(),
                    },
                    selectedItems: () => [
                        {
                            path: "path/to/file.waldiez",
                            name: "file.waldiez",
                        },
                    ],
                },
            },
        } as unknown as IFileBrowserFactory;
        widgetFactory = {} as WaldiezEditorFactory;
        mainMenu = new MainMenu(app.commands);
    });

    it("should register commands", async () => {
        // noinspection DuplicatedCode
        await handleWaldiezCommands(app, tracker, fileBrowserFactory, widgetFactory, mainMenu, undefined);
        expect(app.commands.hasCommand(CommandIDs.createNew)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.openWaldiez)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.exportToPython)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.exportToJupyter)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.interruptKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.restartKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.changeKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.shutdownKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.reconnectToKernel)).toBe(true);
    });

    it("should add commands to the main menu", () => {
        handleWaldiezCommands(app, tracker, fileBrowserFactory, widgetFactory, mainMenu, undefined);
        expect(mainMenu.fileMenu.newMenu.items.some(item => item.command === CommandIDs.createNew)).toBe(
            true,
        );
        expect(mainMenu.kernelMenu.kernelUsers.interruptKernel.ids.includes(CommandIDs.interruptKernel)).toBe(
            true,
        );
        expect(
            mainMenu.kernelMenu.kernelUsers.reconnectToKernel.ids.includes(CommandIDs.reconnectToKernel),
        ).toBe(true);
        expect(mainMenu.kernelMenu.kernelUsers.restartKernel.ids.includes(CommandIDs.restartKernel)).toBe(
            true,
        );
        expect(mainMenu.kernelMenu.kernelUsers.shutdownKernel.ids.includes(CommandIDs.shutdownKernel)).toBe(
            true,
        );
    });

    it("should register commands", async () => {
        jest.mock("../commands", () => {
            const actual = jest.requireActual("../commands");
            return {
                ...actual,
                isWaldiezEditor: jest.fn().mockReturnValue(true),
            };
        });
        await handleWaldiezCommands(app, tracker, fileBrowserFactory, widgetFactory, mainMenu, undefined);
        // noinspection DuplicatedCode
        expect(app.commands.hasCommand(CommandIDs.createNew)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.openWaldiez)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.exportToPython)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.exportToJupyter)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.interruptKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.restartKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.changeKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.shutdownKernel)).toBe(true);
        expect(app.commands.hasCommand(CommandIDs.reconnectToKernel)).toBe(true);
    });
    it("should execute commands", async () => {
        jest.mock("../commands", () => {
            const actual = jest.requireActual("../commands");
            return {
                ...actual,
                isWaldiezEditor: jest.fn().mockReturnValue(true),
            };
        });
        await handleWaldiezCommands(app, tracker, fileBrowserFactory, widgetFactory, mainMenu, undefined);

        // let's skip these two (handle in ui tests)
        // Command 'docmanager:new-untitled' not registered.
        // Command 'docmanager:open' not registered.
        // await app.commands.execute(CommandIDs.createNew);
        // await app.commands.execute(CommandIDs.openWaldiez);
        await app.commands.execute(CommandIDs.exportToPython);
        await app.commands.execute(CommandIDs.exportToJupyter);
        await app.commands.execute(CommandIDs.interruptKernel);
        await app.commands.execute(CommandIDs.restartKernel);
        await app.commands.execute(CommandIDs.changeKernel);
        await app.commands.execute(CommandIDs.shutdownKernel);
        await app.commands.execute(CommandIDs.reconnectToKernel);
    });
});
