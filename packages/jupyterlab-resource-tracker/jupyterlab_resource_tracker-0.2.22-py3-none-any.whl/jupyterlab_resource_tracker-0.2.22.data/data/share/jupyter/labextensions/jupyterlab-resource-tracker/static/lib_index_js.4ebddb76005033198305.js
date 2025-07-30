"use strict";
(self["webpackChunkjupyterlab_resource_tracker"] = self["webpackChunkjupyterlab_resource_tracker"] || []).push([["lib_index_js"],{

/***/ "./lib/components/DashboardComponent.js":
/*!**********************************************!*\
  !*** ./lib/components/DashboardComponent.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_Refresh__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/icons-material/Refresh */ "./node_modules/@mui/icons-material/esm/Refresh.js");
/* harmony import */ var _SummaryComponent__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./SummaryComponent */ "./lib/components/SummaryComponent.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);






const DashboardComponent = () => {
    const [summaryList, setSummaryList] = react__WEBPACK_IMPORTED_MODULE_0___default().useState([]);
    const [loading, setLoading] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        getLogs();
    }, []);
    const getLogs = async () => {
        setLoading(true);
        try {
            const response = await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('usages-costs/logs', {
                method: 'GET'
            });
            if (response) {
                setSummaryList(response.summary);
            }
        }
        catch (error) {
            console.error('Error fetching logs:', error);
            let errorMessage = 'An unexpected error occurred.';
            if (error && error.response && error.response.status) {
                switch (error.response.status) {
                    case 400:
                        errorMessage = 'Invalid log file format. Please check the logs.';
                        break;
                    case 404:
                        errorMessage =
                            'Log files not found. Ensure they exist in the configured path.';
                        break;
                    case 500:
                        console.error('Error response from server:', error.response);
                        errorMessage =
                            'Server error: ' +
                                (error.response.data?.error || 'Unknown issue');
                        break;
                    default:
                        errorMessage = error.response.data?.error || 'Unexpected error.';
                }
            }
            else if (error?.message) {
                errorMessage = error.message;
            }
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.showErrorMessage)('Error Fetching Logs', errorMessage);
        }
        finally {
            setLoading(false);
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.AppBar, { position: "static", color: "primary" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Toolbar, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "h6", sx: { flexGrow: 1 } }, "Dashboard"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tooltip, { title: "Refresh Data" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { color: "inherit", onClick: getLogs, disabled: loading }, loading ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CircularProgress, { size: 24, color: "inherit" })) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_Refresh__WEBPACK_IMPORTED_MODULE_4__["default"], null)))))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: { p: 2, height: '92%', overflowY: 'auto' } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_SummaryComponent__WEBPACK_IMPORTED_MODULE_5__["default"], { summary: summaryList, loading: loading }))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DashboardComponent);


/***/ }),

/***/ "./lib/components/SummaryComponent.js":
/*!********************************************!*\
  !*** ./lib/components/SummaryComponent.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/x-data-grid */ "webpack/sharing/consume/default/@mui/x-data-grid/@mui/x-data-grid");
/* harmony import */ var _mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__);



const SummaryComponent = (props) => {
    const columns = [
        { field: 'id', headerName: 'ID', width: 70 },
        { field: 'project', headerName: 'Project', width: 115 },
        { field: 'podName', headerName: 'Username', width: 105 },
        { field: 'usage', headerName: 'Usage (Hours)', type: 'number', width: 120 },
        {
            field: 'cost',
            headerName: 'Cost',
            type: 'number',
            width: 80
        },
        { field: 'month', headerName: 'Month', width: 60, align: 'center' },
        { field: 'year', headerName: 'Year', width: 60, align: 'center' },
        {
            field: 'lastUpdate',
            headerName: 'Updated',
            width: 135,
            renderCell: (params) => {
                const raw = params.value;
                if (!raw || typeof raw !== 'string') {
                    return '';
                }
                let iso = raw;
                // Truncate microseconds to milliseconds (keeping only 3 digits)
                iso = iso.replace(/(\.\d{3})\d+/, '$1');
                // Convert +00:00 offset to 'Z' for UTC
                if (iso.endsWith('+00:00')) {
                    iso = iso.replace('+00:00', 'Z');
                }
                const date = new Date(iso);
                if (isNaN(date.getTime())) {
                    return '';
                }
                return date.toLocaleString('en-US', {
                    dateStyle: 'short',
                    timeStyle: 'short'
                });
            }
        },
        {
            field: 'user_efs_cost',
            headerName: 'User EFS cost',
            type: 'number',
            width: 140
        },
        {
            field: 'project_efs_cost',
            headerName: 'Project EFS cost',
            type: 'number',
            width: 150
        }
    ];
    const paginationModel = { page: 0, pageSize: 10 };
    function CustomFooter() {
        const apiRef = (0,_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__.useGridApiContext)();
        const rows = (0,_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__.useGridSelector)(apiRef, _mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__.gridFilteredSortedRowEntriesSelector);
        const totalComputeTime = rows.reduce((sum, rowEntry) => sum + (rowEntry.model.usage ?? 0), 0);
        const totalComputeCost = rows.reduce((sum, rowEntry) => sum + (rowEntry.model.cost ?? 0), 0);
        const totalUserStorageCost = rows.reduce((sum, rowEntry) => sum + (rowEntry.model.user_efs_cost ?? 0), 0);
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__.GridFooterContainer, null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: {
                    width: '100%',
                    display: 'flex',
                    justifyContent: 'flex-start',
                    gap: '1rem',
                    paddingLeft: '1rem'
                } },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "subtitle2" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("strong", null, "Total Computed Time (Hours):"),
                    ' ',
                    totalComputeTime.toFixed(2)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "subtitle2" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("strong", null, "Total Computed Cost:"),
                    " ",
                    totalComputeCost.toFixed(2)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "subtitle2" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("strong", null, "Total User EFS Cost:"),
                    ' ',
                    totalUserStorageCost.toFixed(2)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__.GridPagination, null))));
    }
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "h6", gutterBottom: true }, "Monthly costs and usages to date"),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Paper, { sx: { p: 2, boxShadow: 3, borderRadius: 2, mb: 2 } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__.DataGrid, { slots: { footer: CustomFooter }, autoHeight: true, rows: props.summary, columns: columns, loading: props.loading, initialState: {
                    pagination: { paginationModel },
                    columns: {
                        columnVisibilityModel: {
                            id: false
                        }
                    }
                }, pageSizeOptions: [10, 20, 30], disableRowSelectionOnClick: true, sx: { border: 0 } }))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SummaryComponent);


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupyterlab-resource-tracker', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _widgets_DashboardWidget__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./widgets/DashboardWidget */ "./lib/widgets/DashboardWidget.js");
/* harmony import */ var _style_IconsStyle__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./style/IconsStyle */ "./lib/style/IconsStyle.js");






const PLUGIN_ID = 'jupyterlab-resource-tracker:plugin';
const PALETTE_CATEGORY = 'Admin tools';
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.createNew = 'jupyterlab-resource-tracker:open-dashboard';
})(CommandIDs || (CommandIDs = {}));
/**
 * Initialization data for the jupyterlab-resource-tracker extension.
 */
const plugin = {
    id: PLUGIN_ID,
    description: 'A JupyterLab extension.',
    autoStart: true,
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__.ISettingRegistry, _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__.ILauncher, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette],
    activate: (app, settingRegistry, launcher, palette) => {
        console.log('JupyterLab extension jupyterlab-resource-tracker is activated!');
        if (settingRegistry) {
            settingRegistry
                .load(plugin.id)
                .then(settings => {
                console.log('jupyterlab-resource-tracker settings loaded:', settings.composite);
            })
                .catch(reason => {
                console.error('Failed to load settings for jupyterlab-resource-tracker.', reason);
            });
        }
        (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('get-example')
            .then(data => {
            console.log(data);
        })
            .catch(reason => {
            console.error(`The jupyterlab_resource_tracker server extension appears to be missing.\n${reason}`);
        });
        const { commands } = app;
        const command = CommandIDs.createNew;
        // const sideBarContent = new NBQueueSideBarWidget(s3BucketId);
        // const sideBarWidget = new MainAreaWidget<NBQueueSideBarWidget>({
        //   content: sideBarContent
        // });
        // sideBarWidget.toolbar.hide();
        // sideBarWidget.title.icon = runIcon;
        // sideBarWidget.title.caption = 'NBQueue job list';
        // app.shell.add(sideBarWidget, 'right', { rank: 501 });
        // Define a widget creator function,
        // then call it to make a new widget
        const newWidget = () => {
            // Create a blank content widget inside of a MainAreaWidget
            const dashboardContent = new _widgets_DashboardWidget__WEBPACK_IMPORTED_MODULE_4__.DashboardWidget();
            const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.MainAreaWidget({
                content: dashboardContent
            });
            widget.id = 'resource-tracker-dashboard';
            widget.title.label = 'Resource Tracker';
            widget.title.closable = true;
            return widget;
        };
        let widget = newWidget();
        commands.addCommand(command, {
            label: 'Resource Tracker',
            caption: 'Resource Tracker',
            icon: args => (args['isPalette'] ? undefined : _style_IconsStyle__WEBPACK_IMPORTED_MODULE_5__.costTrackerIcon),
            execute: async (args) => {
                console.log('Command executed');
                // Regenerate the widget if disposed
                if (widget.isDisposed) {
                    widget = newWidget();
                }
                if (!widget.isAttached) {
                    // Attach the widget to the main work area if it's not there
                    app.shell.add(widget, 'main');
                }
                // Activate the widget
                app.shell.activateById(widget.id);
            }
        });
        if (launcher) {
            launcher.add({
                command,
                category: 'Admin tools',
                rank: 1
            });
        }
        if (palette) {
            palette.addItem({
                command,
                args: { isPalette: true },
                category: PALETTE_CATEGORY
            });
        }
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/style/IconsStyle.js":
/*!*********************************!*\
  !*** ./lib/style/IconsStyle.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   costTrackerIcon: () => (/* binding */ costTrackerIcon)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _style_cost_tracker_svg__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../style/cost-tracker.svg */ "./style/cost-tracker.svg");


const costTrackerIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'custom:cost-tracker',
    svgstr: _style_cost_tracker_svg__WEBPACK_IMPORTED_MODULE_1__
});


/***/ }),

/***/ "./lib/widgets/DashboardWidget.js":
/*!****************************************!*\
  !*** ./lib/widgets/DashboardWidget.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DashboardWidget: () => (/* binding */ DashboardWidget)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_DashboardComponent__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/DashboardComponent */ "./lib/components/DashboardComponent.js");



class DashboardWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    constructor() {
        super();
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_DashboardComponent__WEBPACK_IMPORTED_MODULE_2__["default"], null));
    }
}


/***/ }),

/***/ "./node_modules/@mui/icons-material/esm/Refresh.js":
/*!*********************************************************!*\
  !*** ./node_modules/@mui/icons-material/esm/Refresh.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_createSvgIcon_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./utils/createSvgIcon.js */ "./node_modules/@mui/material/esm/utils/createSvgIcon.js");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");
"use client";



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ((0,_utils_createSvgIcon_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_0__.jsx)("path", {
  d: "M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4z"
}), 'Refresh'));

/***/ }),

/***/ "./style/cost-tracker.svg":
/*!********************************!*\
  !*** ./style/cost-tracker.svg ***!
  \********************************/
/***/ ((module) => {

module.exports = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!-- Generated by Pixelmator Pro 3.7 -->\n<svg width=\"953\" height=\"1100\" viewBox=\"0 0 953 1100\" xmlns=\"http://www.w3.org/2000/svg\">\n    <g id=\"Agrupar-copia\">\n        <g id=\"Agrupar\">\n            <path id=\"Trazado\" fill=\"#14a0de\" stroke=\"none\" d=\"M 594.294922 260.210083 L 621.234375 260.210083 C 631.294922 260.210083 640.916016 264.499756 647.644531 271.969482 C 654.512695 279.562256 657.704102 289.36145 656.705078 299.600098 C 654.868164 317.458496 638.202148 331.452393 618.78125 331.452393 L 582.179688 331.452393 C 571.379883 331.452393 561.888672 323.817383 559.654297 313.34729 C 558.386719 307.247314 552.788086 302.807007 546.360352 302.807007 L 504.550781 302.807007 C 500.617188 302.807007 496.813477 304.493164 494.141602 307.425293 C 491.605469 310.22229 490.337891 313.936279 490.6875 317.66394 C 495.058594 360.60376 528.515625 394.210205 571.113281 399.376831 L 571.113281 435.642944 C 571.113281 443.235107 577.279297 449.430176 584.893555 449.430176 L 626.223633 449.430176 C 633.830078 449.430176 639.99707 443.235107 639.99707 435.642944 L 639.99707 397.814819 C 686.089844 388.111328 720.860352 351.064941 725.232422 306.302246 C 728.166992 276.40979 718.674805 247.765015 698.603516 225.643799 C 678.785156 203.824219 650.579102 191.311035 621.234375 191.311035 L 589.922852 191.311035 C 579.863281 191.311035 570.194336 187.02124 563.416992 179.52417 C 556.597656 171.958862 553.404297 162.145874 554.453125 151.907227 C 556.249023 133.993896 572.908203 119.986816 592.370117 119.986816 L 628.929688 119.986816 C 639.736328 119.986816 649.179688 127.662598 651.455078 138.215576 C 652.764648 144.341919 658.232422 148.632202 664.75 148.632202 L 706.55957 148.632202 C 710.541016 148.632202 714.34375 146.945557 717.009766 143.972168 C 719.544922 141.175781 720.771484 137.475464 720.381836 133.802246 C 716.049805 90.834961 682.635742 57.242188 639.99707 52.157471 L 639.99707 15.878174 C 639.99707 8.244263 633.830078 2.035889 626.223633 2.035889 L 584.893555 2.035889 C 577.279297 2.035889 571.113281 8.244263 571.113281 15.878174 L 571.113281 52.979492 C 517.674805 62.559937 480.544922 111.297485 485.876953 166.07959 C 491.043945 218.859741 538.665039 260.210083 594.294922 260.210083 Z\"/>\n            <path id=\"path1\" fill=\"#203a72\" stroke=\"none\" d=\"M 151.166016 778.668579 L 26.070313 778.668579 C 12.648438 778.668579 1.762695 789.554688 1.762695 802.983521 L 1.762695 1069.651611 C 1.762695 1083.079956 12.648438 1093.966064 26.070313 1093.966064 L 151.166016 1093.966064 C 164.585938 1093.966064 175.472656 1083.079956 175.472656 1069.651611 L 175.472656 802.983521 C 175.472656 789.554688 164.585938 778.668579 151.166016 778.668579 Z\"/>\n            <path id=\"path2\" fill=\"#203a72\" stroke=\"none\" d=\"M 409.641602 638.322388 L 284.545898 638.322388 C 271.124023 638.322388 260.238281 649.208496 260.238281 662.637695 L 260.238281 1069.651611 C 260.238281 1083.079956 271.124023 1093.966064 284.545898 1093.966064 L 409.641602 1093.966064 C 423.0625 1093.966064 433.947266 1083.079956 433.947266 1069.651611 L 433.947266 662.637695 C 433.947266 649.208496 423.0625 638.322388 409.641602 638.322388 Z\"/>\n            <path id=\"path3\" fill=\"#203a72\" stroke=\"none\" d=\"M 668.110352 778.668579 L 543.013672 778.668579 C 529.592773 778.668579 518.707031 789.554688 518.707031 802.983521 L 518.707031 1069.651611 C 518.707031 1083.079956 529.592773 1093.966064 543.013672 1093.966064 L 668.110352 1093.966064 C 681.530273 1093.966064 692.416016 1083.079956 692.416016 1069.651611 L 692.416016 802.983521 C 692.416016 789.554688 681.530273 778.668579 668.110352 778.668579 Z\"/>\n            <path id=\"path4\" fill=\"#203a72\" stroke=\"none\" d=\"M 926.579102 638.322388 L 801.482422 638.322388 C 788.061523 638.322388 777.175781 649.208496 777.175781 662.637695 L 777.175781 1069.651611 C 777.175781 1083.079956 788.061523 1093.966064 801.482422 1093.966064 L 926.579102 1093.966064 C 939.999023 1093.966064 950.885742 1083.079956 950.885742 1069.651611 L 950.885742 662.637695 C 950.885742 649.208496 939.999023 638.322388 926.579102 638.322388 Z\"/>\n            <path id=\"path5\" fill=\"#14a0de\" stroke=\"none\" d=\"M 812.708984 512.819824 C 826.956055 523.852417 844.616211 530.691895 864.03125 530.691895 C 910.541016 530.691895 948.238281 492.986938 948.238281 446.483765 C 948.238281 399.980591 910.541016 362.276123 864.03125 362.276123 C 817.527344 362.276123 779.822266 399.980591 779.822266 446.483765 C 779.822266 453.11731 780.782227 459.50415 782.228516 465.699219 L 656.882813 546.233521 C 642.635742 535.187134 624.982422 528.347656 605.5625 528.347656 C 586.140625 528.347656 568.487305 535.187134 554.241211 546.233521 L 428.894531 465.699219 C 430.341797 459.50415 431.300781 453.11731 431.300781 446.483765 C 431.300781 399.980591 393.59668 362.276123 347.092773 362.276123 C 300.583008 362.276123 262.885742 399.980591 262.885742 446.483765 C 262.885742 453.11731 263.837891 459.50415 265.291016 465.699219 L 139.945313 546.233521 C 125.699219 535.187134 108.039063 528.347656 88.618164 528.347656 C 42.114258 528.347656 4.410156 566.052612 4.410156 612.555908 C 4.410156 659.072266 42.114258 696.762939 88.618164 696.762939 C 135.12793 696.762939 172.825195 659.072266 172.825195 612.555908 C 172.825195 605.921875 171.873047 599.548706 170.419922 593.353638 L 295.772461 512.819824 C 310.011719 523.852417 327.671875 530.691895 347.092773 530.691895 C 366.506836 530.691895 384.160156 523.852417 398.407227 512.819824 L 523.758789 593.353638 C 522.306641 599.548706 521.354492 605.921875 521.354492 612.555908 C 521.354492 659.072266 559.058594 696.762939 605.5625 696.762939 C 652.066406 696.762939 689.769531 659.072266 689.769531 612.555908 C 689.769531 605.921875 688.817383 599.548706 687.364258 593.353638 L 812.708984 512.819824 Z\"/>\n        </g>\n    </g>\n</svg>\n";

/***/ })

}]);
//# sourceMappingURL=lib_index_js.4ebddb76005033198305.js.map