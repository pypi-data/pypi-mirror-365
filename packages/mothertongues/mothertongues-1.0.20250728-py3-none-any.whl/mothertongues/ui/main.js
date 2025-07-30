(self["webpackChunkmtd_mobile_ui"] = self["webpackChunkmtd_mobile_ui"] || []).push([["main"],{

/***/ 9266:
/*!**************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/app-routing.module.ts ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AppRoutingModule: () => (/* binding */ AppRoutingModule)
/* harmony export */ });
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/router */ 5072);
/* harmony import */ var _environments_environment__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../environments/environment */ 3840);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ 7580);




const routes = [{
  path: '',
  redirectTo: 'search',
  pathMatch: 'full'
}, {
  path: 'search',
  loadChildren: () => Promise.resolve(/*! import() */).then(__webpack_require__.bind(__webpack_require__, /*! ./search/search.module */ 1285)).then(m => m.SearchPageModule)
}, {
  path: 'about',
  loadChildren: () => __webpack_require__.e(/*! import() */ "packages_mtd-mobile-ui_src_app_about_about_module_ts").then(__webpack_require__.bind(__webpack_require__, /*! ./about/about.module */ 9503)).then(m => m.AboutPageModule)
}, {
  path: 'browse',
  loadChildren: () => __webpack_require__.e(/*! import() */ "packages_mtd-mobile-ui_src_app_browse_browse_module_ts").then(__webpack_require__.bind(__webpack_require__, /*! ./browse/browse.module */ 4925)).then(m => m.BrowsePageModule)
}, {
  path: 'bookmarks',
  loadChildren: () => __webpack_require__.e(/*! import() */ "packages_mtd-mobile-ui_src_app_bookmarks_bookmarks_module_ts").then(__webpack_require__.bind(__webpack_require__, /*! ./bookmarks/bookmarks.module */ 547)).then(m => m.BookmarksPageModule)
}, {
  path: 'flashcards',
  loadChildren: () => __webpack_require__.e(/*! import() */ "packages_mtd-mobile-ui_src_app_flashcards_flashcards_module_ts").then(__webpack_require__.bind(__webpack_require__, /*! ./flashcards/flashcards.module */ 3879)).then(m => m.FlashcardsPageModule)
}];
class AppRoutingModule {
  static #_ = this.ɵfac = function AppRoutingModule_Factory(t) {
    return new (t || AppRoutingModule)();
  };
  static #_2 = this.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineNgModule"]({
    type: AppRoutingModule
  });
  static #_3 = this.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineInjector"]({
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule.forRoot(routes, {
      preloadingStrategy: _angular_router__WEBPACK_IMPORTED_MODULE_2__.PreloadAllModules,
      useHash: _environments_environment__WEBPACK_IMPORTED_MODULE_0__.environment.useHash
    }), _angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule]
  });
}
(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵsetNgModuleScope"](AppRoutingModule, {
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule],
    exports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule]
  });
})();

/***/ }),

/***/ 6828:
/*!*********************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/app.component.ts ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AppComponent: () => (/* binding */ AppComponent)
/* harmony export */ });
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./data.service */ 5329);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ 7580);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/router */ 5072);






const _c0 = a0 => [a0];
function AppComponent_ion_menu_toggle_9_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "ion-menu-toggle", 5)(1, "ion-item", 6);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelement"](2, "ion-icon", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](3, "ion-label");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](4);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()()();
  }
  if (rf & 2) {
    const p_r1 = ctx.$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("routerLink", _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵpureFunction1"](4, _c0, p_r1.url));
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ios", p_r1.icon + "-outline")("md", p_r1.icon + "-sharp");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtextInterpolate"](p_r1.title);
  }
}
class AppComponent {
  constructor(dataService) {
    this.dataService = dataService;
    this.appPages = [{
      title: 'Search',
      url: '/search',
      icon: 'search'
    }, {
      title: 'Browse',
      url: '/browse',
      icon: ''
    }, {
      title: 'Bookmarks',
      url: '/bookmarks',
      icon: 'bookmark'
    }, {
      title: 'Flashcards',
      url: '/flashcards',
      icon: ''
    }, {
      title: 'About',
      url: '/about',
      icon: 'information-circle'
    }];
    this.title = 'Mother Tongues Dictionary';
  }
  ngOnInit() {
    this.dataService.$config.subscribe(config => {
      if (config) {
        this.title = config.L1;
      }
    });
  }
  static #_ = this.ɵfac = function AppComponent_Factory(t) {
    return new (t || AppComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdirectiveInject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService));
  };
  static #_2 = this.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineComponent"]({
    type: AppComponent,
    selectors: [["mtd-root"]],
    decls: 11,
    vars: 2,
    consts: [["contentId", "main-content"], ["contentId", "main-content", "type", "overlay"], ["id", "inbox-list"], ["auto-hide", "false", 4, "ngFor", "ngForOf"], ["id", "main-content"], ["auto-hide", "false"], ["routerDirection", "root", "lines", "none", "detail", "false", "routerLinkActive", "selected", 3, "routerLink"], ["aria-hidden", "true", "slot", "start", 3, "ios", "md"]],
    template: function AppComponent_Template(rf, ctx) {
      if (rf & 1) {
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "ion-app")(1, "ion-split-pane", 0)(2, "ion-menu", 1)(3, "ion-content")(4, "ion-list", 2)(5, "ion-list-header");
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6);
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](7, "ion-note");
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](8, "Welcome!");
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](9, AppComponent_ion_menu_toggle_9_Template, 5, 6, "ion-menu-toggle", 3);
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()()();
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelement"](10, "ion-router-outlet", 4);
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
      }
      if (rf & 2) {
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](6);
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtextInterpolate"](ctx.title);
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](3);
        _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngForOf", ctx.appPages);
      }
    },
    dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_2__.NgForOf, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonApp, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonContent, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonIcon, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonItem, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonLabel, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonList, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonListHeader, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonMenu, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonMenuToggle, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonNote, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonSplitPane, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.IonRouterOutlet, _ionic_angular__WEBPACK_IMPORTED_MODULE_3__.RouterLinkDelegate, _angular_router__WEBPACK_IMPORTED_MODULE_4__.RouterLink, _angular_router__WEBPACK_IMPORTED_MODULE_4__.RouterLinkActive],
    styles: ["ion-menu[_ngcontent-%COMP%]   ion-content[_ngcontent-%COMP%] {\n  --background: var(--ion-item-background, var(--ion-background-color, #fff));\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-content[_ngcontent-%COMP%] {\n  --padding-start: 8px;\n  --padding-end: 8px;\n  --padding-top: 20px;\n  --padding-bottom: 20px;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-list[_ngcontent-%COMP%] {\n  padding: 20px 0;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-note[_ngcontent-%COMP%] {\n  margin-bottom: 30px;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-list-header[_ngcontent-%COMP%], ion-menu.md[_ngcontent-%COMP%]   ion-note[_ngcontent-%COMP%] {\n  padding-left: 10px;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-list#inbox-list[_ngcontent-%COMP%] {\n  border-bottom: 1px solid var(--ion-color-step-150, #d7d8da);\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-list#inbox-list[_ngcontent-%COMP%]   ion-list-header[_ngcontent-%COMP%] {\n  font-size: 22px;\n  font-weight: 600;\n  min-height: 20px;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-list#labels-list[_ngcontent-%COMP%]   ion-list-header[_ngcontent-%COMP%] {\n  font-size: 16px;\n  margin-bottom: 18px;\n  color: #757575;\n  min-height: 26px;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-item[_ngcontent-%COMP%] {\n  --padding-start: 10px;\n  --padding-end: 10px;\n  border-radius: 4px;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-item.selected[_ngcontent-%COMP%] {\n  --background: rgba(var(--ion-color-primary-rgb), 0.14);\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-item.selected[_ngcontent-%COMP%]   ion-icon[_ngcontent-%COMP%] {\n  color: var(--ion-color-primary);\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-item[_ngcontent-%COMP%]   ion-icon[_ngcontent-%COMP%] {\n  color: #616e7e;\n}\n\nion-menu.md[_ngcontent-%COMP%]   ion-item[_ngcontent-%COMP%]   ion-label[_ngcontent-%COMP%] {\n  font-weight: 500;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-content[_ngcontent-%COMP%] {\n  --padding-bottom: 20px;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-list[_ngcontent-%COMP%] {\n  padding: 20px 0 0 0;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-note[_ngcontent-%COMP%] {\n  line-height: 24px;\n  margin-bottom: 20px;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-item[_ngcontent-%COMP%] {\n  --padding-start: 16px;\n  --padding-end: 16px;\n  --min-height: 50px;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-item.selected[_ngcontent-%COMP%]   ion-icon[_ngcontent-%COMP%] {\n  color: var(--ion-color-primary);\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-item[_ngcontent-%COMP%]   ion-icon[_ngcontent-%COMP%] {\n  font-size: 24px;\n  color: #73849a;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-list#labels-list[_ngcontent-%COMP%]   ion-list-header[_ngcontent-%COMP%] {\n  margin-bottom: 8px;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-list-header[_ngcontent-%COMP%], ion-menu.ios[_ngcontent-%COMP%]   ion-note[_ngcontent-%COMP%] {\n  padding-left: 16px;\n  padding-right: 16px;\n}\n\nion-menu.ios[_ngcontent-%COMP%]   ion-note[_ngcontent-%COMP%] {\n  margin-bottom: 8px;\n}\n\nion-note[_ngcontent-%COMP%] {\n  display: inline-block;\n  font-size: 16px;\n  color: var(--ion-color-medium-shade);\n}\n\nion-item.selected[_ngcontent-%COMP%] {\n  --color: var(--ion-color-primary);\n}\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3BhY2thZ2VzL210ZC1tb2JpbGUtdWkvc3JjL2FwcC9hcHAuY29tcG9uZW50LnNjc3MiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7RUFDRSwyRUFBQTtBQUNGOztBQUVBO0VBQ0Usb0JBQUE7RUFDQSxrQkFBQTtFQUNBLG1CQUFBO0VBQ0Esc0JBQUE7QUFDRjs7QUFFQTtFQUNFLGVBQUE7QUFDRjs7QUFFQTtFQUNFLG1CQUFBO0FBQ0Y7O0FBRUE7O0VBRUUsa0JBQUE7QUFDRjs7QUFFQTtFQUNFLDJEQUFBO0FBQ0Y7O0FBRUE7RUFDRSxlQUFBO0VBQ0EsZ0JBQUE7RUFFQSxnQkFBQTtBQUFGOztBQUdBO0VBQ0UsZUFBQTtFQUVBLG1CQUFBO0VBRUEsY0FBQTtFQUVBLGdCQUFBO0FBSEY7O0FBTUE7RUFDRSxxQkFBQTtFQUNBLG1CQUFBO0VBQ0Esa0JBQUE7QUFIRjs7QUFNQTtFQUNFLHNEQUFBO0FBSEY7O0FBTUE7RUFDRSwrQkFBQTtBQUhGOztBQU1BO0VBQ0UsY0FBQTtBQUhGOztBQU1BO0VBQ0UsZ0JBQUE7QUFIRjs7QUFNQTtFQUNFLHNCQUFBO0FBSEY7O0FBTUE7RUFDRSxtQkFBQTtBQUhGOztBQU1BO0VBQ0UsaUJBQUE7RUFDQSxtQkFBQTtBQUhGOztBQU1BO0VBQ0UscUJBQUE7RUFDQSxtQkFBQTtFQUNBLGtCQUFBO0FBSEY7O0FBTUE7RUFDRSwrQkFBQTtBQUhGOztBQU1BO0VBQ0UsZUFBQTtFQUNBLGNBQUE7QUFIRjs7QUFNQTtFQUNFLGtCQUFBO0FBSEY7O0FBTUE7O0VBRUUsa0JBQUE7RUFDQSxtQkFBQTtBQUhGOztBQU1BO0VBQ0Usa0JBQUE7QUFIRjs7QUFNQTtFQUNFLHFCQUFBO0VBQ0EsZUFBQTtFQUVBLG9DQUFBO0FBSkY7O0FBT0E7RUFDRSxpQ0FBQTtBQUpGIiwic291cmNlc0NvbnRlbnQiOlsiaW9uLW1lbnUgaW9uLWNvbnRlbnQge1xuICAtLWJhY2tncm91bmQ6IHZhcigtLWlvbi1pdGVtLWJhY2tncm91bmQsIHZhcigtLWlvbi1iYWNrZ3JvdW5kLWNvbG9yLCAjZmZmKSk7XG59XG5cbmlvbi1tZW51Lm1kIGlvbi1jb250ZW50IHtcbiAgLS1wYWRkaW5nLXN0YXJ0OiA4cHg7XG4gIC0tcGFkZGluZy1lbmQ6IDhweDtcbiAgLS1wYWRkaW5nLXRvcDogMjBweDtcbiAgLS1wYWRkaW5nLWJvdHRvbTogMjBweDtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWxpc3Qge1xuICBwYWRkaW5nOiAyMHB4IDA7XG59XG5cbmlvbi1tZW51Lm1kIGlvbi1ub3RlIHtcbiAgbWFyZ2luLWJvdHRvbTogMzBweDtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWxpc3QtaGVhZGVyLFxuaW9uLW1lbnUubWQgaW9uLW5vdGUge1xuICBwYWRkaW5nLWxlZnQ6IDEwcHg7XG59XG5cbmlvbi1tZW51Lm1kIGlvbi1saXN0I2luYm94LWxpc3Qge1xuICBib3JkZXItYm90dG9tOiAxcHggc29saWQgdmFyKC0taW9uLWNvbG9yLXN0ZXAtMTUwLCAjZDdkOGRhKTtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWxpc3QjaW5ib3gtbGlzdCBpb24tbGlzdC1oZWFkZXIge1xuICBmb250LXNpemU6IDIycHg7XG4gIGZvbnQtd2VpZ2h0OiA2MDA7XG5cbiAgbWluLWhlaWdodDogMjBweDtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWxpc3QjbGFiZWxzLWxpc3QgaW9uLWxpc3QtaGVhZGVyIHtcbiAgZm9udC1zaXplOiAxNnB4O1xuXG4gIG1hcmdpbi1ib3R0b206IDE4cHg7XG5cbiAgY29sb3I6ICM3NTc1NzU7XG5cbiAgbWluLWhlaWdodDogMjZweDtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWl0ZW0ge1xuICAtLXBhZGRpbmctc3RhcnQ6IDEwcHg7XG4gIC0tcGFkZGluZy1lbmQ6IDEwcHg7XG4gIGJvcmRlci1yYWRpdXM6IDRweDtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWl0ZW0uc2VsZWN0ZWQge1xuICAtLWJhY2tncm91bmQ6IHJnYmEodmFyKC0taW9uLWNvbG9yLXByaW1hcnktcmdiKSwgMC4xNCk7XG59XG5cbmlvbi1tZW51Lm1kIGlvbi1pdGVtLnNlbGVjdGVkIGlvbi1pY29uIHtcbiAgY29sb3I6IHZhcigtLWlvbi1jb2xvci1wcmltYXJ5KTtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWl0ZW0gaW9uLWljb24ge1xuICBjb2xvcjogIzYxNmU3ZTtcbn1cblxuaW9uLW1lbnUubWQgaW9uLWl0ZW0gaW9uLWxhYmVsIHtcbiAgZm9udC13ZWlnaHQ6IDUwMDtcbn1cblxuaW9uLW1lbnUuaW9zIGlvbi1jb250ZW50IHtcbiAgLS1wYWRkaW5nLWJvdHRvbTogMjBweDtcbn1cblxuaW9uLW1lbnUuaW9zIGlvbi1saXN0IHtcbiAgcGFkZGluZzogMjBweCAwIDAgMDtcbn1cblxuaW9uLW1lbnUuaW9zIGlvbi1ub3RlIHtcbiAgbGluZS1oZWlnaHQ6IDI0cHg7XG4gIG1hcmdpbi1ib3R0b206IDIwcHg7XG59XG5cbmlvbi1tZW51LmlvcyBpb24taXRlbSB7XG4gIC0tcGFkZGluZy1zdGFydDogMTZweDtcbiAgLS1wYWRkaW5nLWVuZDogMTZweDtcbiAgLS1taW4taGVpZ2h0OiA1MHB4O1xufVxuXG5pb24tbWVudS5pb3MgaW9uLWl0ZW0uc2VsZWN0ZWQgaW9uLWljb24ge1xuICBjb2xvcjogdmFyKC0taW9uLWNvbG9yLXByaW1hcnkpO1xufVxuXG5pb24tbWVudS5pb3MgaW9uLWl0ZW0gaW9uLWljb24ge1xuICBmb250LXNpemU6IDI0cHg7XG4gIGNvbG9yOiAjNzM4NDlhO1xufVxuXG5pb24tbWVudS5pb3MgaW9uLWxpc3QjbGFiZWxzLWxpc3QgaW9uLWxpc3QtaGVhZGVyIHtcbiAgbWFyZ2luLWJvdHRvbTogOHB4O1xufVxuXG5pb24tbWVudS5pb3MgaW9uLWxpc3QtaGVhZGVyLFxuaW9uLW1lbnUuaW9zIGlvbi1ub3RlIHtcbiAgcGFkZGluZy1sZWZ0OiAxNnB4O1xuICBwYWRkaW5nLXJpZ2h0OiAxNnB4O1xufVxuXG5pb24tbWVudS5pb3MgaW9uLW5vdGUge1xuICBtYXJnaW4tYm90dG9tOiA4cHg7XG59XG5cbmlvbi1ub3RlIHtcbiAgZGlzcGxheTogaW5saW5lLWJsb2NrO1xuICBmb250LXNpemU6IDE2cHg7XG5cbiAgY29sb3I6IHZhcigtLWlvbi1jb2xvci1tZWRpdW0tc2hhZGUpO1xufVxuXG5pb24taXRlbS5zZWxlY3RlZCB7XG4gIC0tY29sb3I6IHZhcigtLWlvbi1jb2xvci1wcmltYXJ5KTtcbn1cbiJdLCJzb3VyY2VSb290IjoiIn0= */"]
  });
}

/***/ }),

/***/ 5451:
/*!******************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/app.module.ts ***!
  \******************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AppModule: () => (/* binding */ AppModule)
/* harmony export */ });
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @angular/platform-browser */ 436);
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/router */ 5072);
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./data.service */ 5329);
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @angular/common/http */ 6443);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @ionic/angular */ 4059);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./app.component */ 6828);
/* harmony import */ var _app_routing_module__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./app-routing.module */ 9266);
/* harmony import */ var _search_search_module__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./search/search.module */ 1285);
/* harmony import */ var _shared_shared_module__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./shared/shared.module */ 3023);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/core */ 7580);











class AppModule {
  static #_ = this.ɵfac = function AppModule_Factory(t) {
    return new (t || AppModule)();
  };
  static #_2 = this.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_5__["ɵɵdefineNgModule"]({
    type: AppModule,
    bootstrap: [_app_component__WEBPACK_IMPORTED_MODULE_1__.AppComponent]
  });
  static #_3 = this.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_5__["ɵɵdefineInjector"]({
    providers: [{
      provide: _angular_router__WEBPACK_IMPORTED_MODULE_6__.RouteReuseStrategy,
      useClass: _ionic_angular__WEBPACK_IMPORTED_MODULE_7__.IonicRouteStrategy
    }, _data_service__WEBPACK_IMPORTED_MODULE_0__.DataService],
    imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_8__.BrowserModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_9__.IonicModule.forRoot(), _app_routing_module__WEBPACK_IMPORTED_MODULE_2__.AppRoutingModule, _angular_common_http__WEBPACK_IMPORTED_MODULE_10__.HttpClientModule, _search_search_module__WEBPACK_IMPORTED_MODULE_3__.SearchPageModule, _shared_shared_module__WEBPACK_IMPORTED_MODULE_4__.SharedModule]
  });
}
(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_5__["ɵɵsetNgModuleScope"](AppModule, {
    declarations: [_app_component__WEBPACK_IMPORTED_MODULE_1__.AppComponent],
    imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_8__.BrowserModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_9__.IonicModule, _app_routing_module__WEBPACK_IMPORTED_MODULE_2__.AppRoutingModule, _angular_common_http__WEBPACK_IMPORTED_MODULE_10__.HttpClientModule, _search_search_module__WEBPACK_IMPORTED_MODULE_3__.SearchPageModule, _shared_shared_module__WEBPACK_IMPORTED_MODULE_4__.SharedModule]
  });
})();

/***/ }),

/***/ 5329:
/*!********************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/data.service.ts ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DataService: () => (/* binding */ DataService)
/* harmony export */ });
/* harmony import */ var _mothertongues_search__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mothertongues/search */ 9355);
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! rxjs */ 5797);
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! rxjs */ 4334);
/* harmony import */ var _environments_environment__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../environments/environment */ 3840);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/core */ 7580);
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/common/http */ 6443);






class DataService {
  constructor(http) {
    this.http = http;
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    this.$entriesHash = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject({});
    this.$entriesLength = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject(0);
    this.$loaded = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject(false);
    this.$config = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject(null);
    this.$sortedEntries = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject([]);
    this.$categorizedEntries = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject({});
    this.$categories = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject([]);
    this.$bookmarks = new rxjs__WEBPACK_IMPORTED_MODULE_2__.BehaviorSubject([]);
    this.http.get(_environments_environment__WEBPACK_IMPORTED_MODULE_1__.environment.dataPath).pipe((0,rxjs__WEBPACK_IMPORTED_MODULE_3__.take)(1)).subscribe(data => {
      const mtdData = data;
      // Load config
      const {
        config
      } = mtdData;
      this.$config.next(config);
      this.$entriesLength.next(mtdData.data.length);
      // Load entries into hash
      const entriesHash = {};
      mtdData.data.forEach(entry => {
        entriesHash[entry.entryID] = entry;
      });
      this.$entriesHash.next(entriesHash);
      // Create Sorted Entries
      this.$sortedEntries.next(Object.values(mtdData.data));
      // Create Categorized Entries
      const categorizedEntries = {
        All: []
      };
      const themes = [];
      const sources = [];
      this.$sortedEntries.value.forEach(entry => {
        if (entry.theme && entry.theme !== 'null') {
          if (entry.theme in categorizedEntries) {
            categorizedEntries[entry.theme].push(entry);
          } else {
            categorizedEntries[entry.theme] = [entry];
            themes.push(entry.theme);
          }
        }
        if (entry.source) {
          if (entry.source in categorizedEntries) {
            categorizedEntries[entry.source].push(entry);
          } else {
            categorizedEntries[entry.source] = [entry];
            sources.push(entry.source);
          }
        }
        categorizedEntries['All'].push(entry);
      });
      sources.sort();
      themes.sort();
      this.$categories.next(['All'].concat(sources).concat(themes));
      this.$categorizedEntries.next(categorizedEntries);
      // Load Searchers
      [this.l1_search, this.l2_search] = (0,_mothertongues_search__WEBPACK_IMPORTED_MODULE_0__.constructSearchers)(mtdData);
      this.$loaded.next(true);
    });
  }
  search_l1(query) {
    return this.l1_search.search(query);
  }
  search_l2(query) {
    return this.l2_search.search(query, 0);
  }
  static #_ = this.ɵfac = function DataService_Factory(t) {
    return new (t || DataService)(_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵinject"](_angular_common_http__WEBPACK_IMPORTED_MODULE_5__.HttpClient));
  };
  static #_2 = this.ɵprov = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineInjectable"]({
    token: DataService,
    factory: DataService.ɵfac,
    providedIn: 'root'
  });
}

/***/ }),

/***/ 292:
/*!************************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/search/search-routing.module.ts ***!
  \************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SearchPageRoutingModule: () => (/* binding */ SearchPageRoutingModule)
/* harmony export */ });
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/router */ 5072);
/* harmony import */ var _search_page__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./search.page */ 9454);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ 7580);




const routes = [{
  path: '',
  component: _search_page__WEBPACK_IMPORTED_MODULE_0__.SearchPage
}];
class SearchPageRoutingModule {
  static #_ = this.ɵfac = function SearchPageRoutingModule_Factory(t) {
    return new (t || SearchPageRoutingModule)();
  };
  static #_2 = this.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineNgModule"]({
    type: SearchPageRoutingModule
  });
  static #_3 = this.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineInjector"]({
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule.forChild(routes), _angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule]
  });
}
(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵsetNgModuleScope"](SearchPageRoutingModule, {
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule],
    exports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule]
  });
})();

/***/ }),

/***/ 1285:
/*!****************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/search/search.module.ts ***!
  \****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SearchPageModule: () => (/* binding */ SearchPageModule)
/* harmony export */ });
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/forms */ 4456);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _search_routing_module__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./search-routing.module */ 292);
/* harmony import */ var _search_page__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./search.page */ 9454);
/* harmony import */ var _shared_shared_module__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../shared/shared.module */ 3023);
/* harmony import */ var _search_service__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./search.service */ 7878);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/core */ 7580);








class SearchPageModule {
  static #_ = this.ɵfac = function SearchPageModule_Factory(t) {
    return new (t || SearchPageModule)();
  };
  static #_2 = this.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineNgModule"]({
    type: SearchPageModule
  });
  static #_3 = this.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineInjector"]({
    providers: [_search_service__WEBPACK_IMPORTED_MODULE_3__.SearchService],
    imports: [_angular_common__WEBPACK_IMPORTED_MODULE_5__.CommonModule, _angular_forms__WEBPACK_IMPORTED_MODULE_6__.FormsModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_7__.IonicModule, _search_routing_module__WEBPACK_IMPORTED_MODULE_0__.SearchPageRoutingModule, _shared_shared_module__WEBPACK_IMPORTED_MODULE_2__.SharedModule]
  });
}
(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵsetNgModuleScope"](SearchPageModule, {
    declarations: [_search_page__WEBPACK_IMPORTED_MODULE_1__.SearchPage],
    imports: [_angular_common__WEBPACK_IMPORTED_MODULE_5__.CommonModule, _angular_forms__WEBPACK_IMPORTED_MODULE_6__.FormsModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_7__.IonicModule, _search_routing_module__WEBPACK_IMPORTED_MODULE_0__.SearchPageRoutingModule, _shared_shared_module__WEBPACK_IMPORTED_MODULE_2__.SharedModule]
  });
})();

/***/ }),

/***/ 9454:
/*!**************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/search/search.page.ts ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SearchPage: () => (/* binding */ SearchPage)
/* harmony export */ });
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../data.service */ 5329);
/* harmony import */ var _mothertongues_search__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mothertongues/search */ 9355);
/* harmony import */ var _search_service__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./search.service */ 7878);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/core */ 7580);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _shared_search_entry_list_component__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../shared/search-entry-list.component */ 2155);









function SearchPage_ion_spinner_9_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelement"](0, "ion-spinner");
  }
}
function SearchPage_div_11_div_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](0, "div", 4)(1, "h4");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](2, "Matches");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelement"](3, "mtd-search-entry-list", 5);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("entries", ctx_r0.searchService.matches)("searchterm", ctx_r0.searchService.searchQuery)("threshold", 0);
  }
}
function SearchPage_div_11_div_2_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](0, "div", 4)(1, "h4");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](2, "Partial Matches");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelement"](3, "mtd-search-entry-list", 5);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("entries", ctx_r0.searchService.partMatches)("searchterm", ctx_r0.searchService.searchQuery)("threshold", ctx_r0.partialThreshold);
  }
}
function SearchPage_div_11_div_3_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](0, "div", 4)(1, "h4");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](2, "Maybe you meant this?");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelement"](3, "mtd-search-entry-list", 5);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("entries", ctx_r0.searchService.maybeMatches)("searchterm", ctx_r0.searchService.searchQuery)("threshold", ctx_r0.maybeThreshold);
  }
}
function SearchPage_div_11_div_4_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](0, "div", 4)(1, "h6");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtextInterpolate1"](" Sorry, we couldn't find any words matching '", ctx_r0.searchService.searchQuery, "'. Please try something else. ");
  }
}
function SearchPage_div_11_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](0, "div");
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtemplate"](1, SearchPage_div_11_div_1_Template, 4, 3, "div", 3)(2, SearchPage_div_11_div_2_Template, 4, 3, "div", 3)(3, SearchPage_div_11_div_3_Template, 4, 3, "div", 3)(4, SearchPage_div_11_div_4_Template, 3, 1, "div", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("ngIf", ctx_r0.searchService.matches.length > 0);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("ngIf", ctx_r0.searchService.partMatches.length > 0);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("ngIf", ctx_r0.searchService.maybeMatches.length > 0);
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("ngIf", ctx_r0.searchService.matches.length === 0 && ctx_r0.searchService.partMatches.length === 0 && ctx_r0.searchService.maybeMatches.length === 0);
  }
}
class SearchPage {
  constructor(dataService, searchService) {
    this.dataService = dataService;
    this.searchService = searchService;
    this.partialThreshold = 1;
    this.maybeThreshold = 2;
    this.$loaded = this.dataService.$loaded;
  }
  ngOnInit() {}
  search(ev) {
    if (ev.target === null) {
      return;
    }
    const query = ev.target.value;
    this.searchService.searchQuery = query;
    if (query.length > 1) {
      let t0 = Date.now();
      // TODO: should be a better way to join results, this could have duplicates
      const l1_results = this.dataService.search_l1(query);
      let t1 = Date.now();
      console.log(`Performed L1 search of ${this.dataService.$entriesLength.value} entries in ${(t1 - t0).toString()} ms`);
      t0 = Date.now();
      const l2_results = this.dataService.search_l2(query);
      t1 = Date.now();
      console.log(`Performed L2 search of ${this.dataService.$entriesLength.value} entries in ${(t1 - t0).toString()} ms`);
      const results = l1_results.concat(l2_results);
      console.log((0,_mothertongues_search__WEBPACK_IMPORTED_MODULE_1__.sortResults)(results));
      this.searchService.matches = (0,_mothertongues_search__WEBPACK_IMPORTED_MODULE_1__.sortResults)(results.filter(result => result[0] < this.partialThreshold));
      this.searchService.partMatches = (0,_mothertongues_search__WEBPACK_IMPORTED_MODULE_1__.sortResults)(results.filter(result => result[0] >= this.partialThreshold && result[0] < this.maybeThreshold));
      this.searchService.maybeMatches = (0,_mothertongues_search__WEBPACK_IMPORTED_MODULE_1__.sortResults)(results.filter(result => result[0] >= this.maybeThreshold));
    }
  }
  static #_ = this.ɵfac = function SearchPage_Factory(t) {
    return new (t || SearchPage)(_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdirectiveInject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService), _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdirectiveInject"](_search_service__WEBPACK_IMPORTED_MODULE_2__.SearchService));
  };
  static #_2 = this.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineComponent"]({
    type: SearchPage,
    selectors: [["mtd-search"]],
    decls: 12,
    vars: 8,
    consts: [["slot", "start"], ["id", "searchBar", "color", "primary", "animated", "true", "placeholder", "Type your word here", 3, "ionInput", "value", "disabled"], [4, "ngIf"], ["class", "result-container", 4, "ngIf"], [1, "result-container"], [3, "entries", "searchterm", "threshold"]],
    template: function SearchPage_Template(rf, ctx) {
      if (rf & 1) {
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](0, "ion-header")(1, "ion-toolbar")(2, "ion-buttons", 0);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelement"](3, "ion-menu-button");
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](4, "ion-title");
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](5, "Search");
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]()()();
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](6, "ion-content")(7, "ion-searchbar", 1);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵpipe"](8, "async");
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵlistener"]("ionInput", function SearchPage_Template_ion_searchbar_ionInput_7_listener($event) {
          return ctx.search($event);
        });
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtemplate"](9, SearchPage_ion_spinner_9_Template, 1, 0, "ion-spinner", 2);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵpipe"](10, "async");
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtemplate"](11, SearchPage_div_11_Template, 5, 4, "div", 2);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
      }
      if (rf & 2) {
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](7);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("value", ctx.searchService.searchQuery)("disabled", _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵpipeBind1"](8, 4, ctx.$loaded) === false);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](2);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("ngIf", _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵpipeBind1"](10, 6, ctx.$loaded) === false);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](2);
        _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("ngIf", ctx.searchService.searchQuery.length > 1);
      }
    },
    dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_5__.NgIf, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonButtons, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonContent, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonHeader, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonMenuButton, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonSearchbar, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonSpinner, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonTitle, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.IonToolbar, _ionic_angular__WEBPACK_IMPORTED_MODULE_6__.TextValueAccessor, _shared_search_entry_list_component__WEBPACK_IMPORTED_MODULE_3__.SearchEntryListComponent, _angular_common__WEBPACK_IMPORTED_MODULE_5__.AsyncPipe],
    styles: ["h4[_ngcontent-%COMP%] {\n  text-align: center;\n}\n\n.result-container[_ngcontent-%COMP%] {\n  margin-top: 3em;\n}\n\n#searchBar[_ngcontent-%COMP%] {\n  width: 75%;\n  margin: 2em auto;\n}\n\nion-label[_ngcontent-%COMP%] {\n  text-align: center;\n}\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3BhY2thZ2VzL210ZC1tb2JpbGUtdWkvc3JjL2FwcC9zZWFyY2gvc2VhcmNoLnBhZ2Uuc2NzcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTtFQUNJLGtCQUFBO0FBQ0o7O0FBRUE7RUFDSSxlQUFBO0FBQ0o7O0FBRUE7RUFDSSxVQUFBO0VBQ0EsZ0JBQUE7QUFDSjs7QUFFQTtFQUNJLGtCQUFBO0FBQ0oiLCJzb3VyY2VzQ29udGVudCI6WyJoNCB7XG4gICAgdGV4dC1hbGlnbjogY2VudGVyXG59XG5cbi5yZXN1bHQtY29udGFpbmVyIHtcbiAgICBtYXJnaW4tdG9wOiAzZW07XG59XG5cbiNzZWFyY2hCYXIge1xuICAgIHdpZHRoOiA3NSU7XG4gICAgbWFyZ2luOiAyZW0gYXV0bztcbn1cblxuaW9uLWxhYmVsIHtcbiAgICB0ZXh0LWFsaWduOiBjZW50ZXI7XG59Il0sInNvdXJjZVJvb3QiOiIifQ== */"]
  });
}

/***/ }),

/***/ 7878:
/*!*****************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/search/search.service.ts ***!
  \*****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SearchService: () => (/* binding */ SearchService)
/* harmony export */ });
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../data.service */ 5329);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ 7580);



class SearchService {
  constructor(dataService) {
    this.dataService = dataService;
    this.searchQuery = '';
    this.matches = [];
    this.partMatches = [];
    this.maybeMatches = [];
  }
  static #_ = this.ɵfac = function SearchService_Factory(t) {
    return new (t || SearchService)(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵinject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService));
  };
  static #_2 = this.ɵprov = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineInjectable"]({
    token: SearchService,
    factory: SearchService.ɵfac,
    providedIn: 'root'
  });
}

/***/ }),

/***/ 7530:
/*!***********************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/shared/entry-list.component.ts ***!
  \***********************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   EntryListComponent: () => (/* binding */ EntryListComponent)
/* harmony export */ });
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../data.service */ 5329);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ 7580);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _entry_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./entry.component */ 4247);






function EntryListComponent_ion_list_1_div_1_ion_item_1_ion_checkbox_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](0, "ion-checkbox", 10);
  }
  if (rf & 2) {
    const entry_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().$implicit;
    const entriesHash_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().ngIf;
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("checked", entriesHash_r3[entry_r2]["checked"]);
  }
}
function EntryListComponent_ion_list_1_div_1_ion_item_1_Template(rf, ctx) {
  if (rf & 1) {
    const _r1 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-item", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function EntryListComponent_ion_list_1_div_1_ion_item_1_Template_ion_item_click_0_listener() {
      const entry_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r1).$implicit;
      const entriesHash_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().ngIf;
      const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r3.showModal(entriesHash_r3[entry_r2]));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, EntryListComponent_ion_list_1_div_1_ion_item_1_ion_checkbox_1_Template, 1, 1, "ion-checkbox", 5);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "ion-label")(3, "div", 6)(4, "span", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](5);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](6, "div", 8)(7, "span", 9);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](8);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
  }
  if (rf & 2) {
    const entry_r2 = ctx.$implicit;
    const entriesHash_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().ngIf;
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r3.edit);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](entriesHash_r3[entry_r2].word);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](entriesHash_r3[entry_r2].definition);
  }
}
function EntryListComponent_ion_list_1_div_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "div");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, EntryListComponent_ion_list_1_div_1_ion_item_1_Template, 9, 3, "ion-item", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngForOf", ctx_r3.entryIDS);
  }
}
function EntryListComponent_ion_list_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-list");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, EntryListComponent_ion_list_1_div_1_Template, 2, 1, "div", 1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipe"](2, "async");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipeBind1"](2, 1, ctx_r3.$entriesHash));
  }
}
function EntryListComponent_ng_template_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r5 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-header")(1, "ion-toolbar");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](2, "ion-title");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](3, "ion-buttons", 11)(4, "ion-button", 12);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function EntryListComponent_ng_template_3_Template_ion_button_click_4_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r5);
      const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r3.isModalOpen = false);
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](5, "Close");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](6, "ion-content", 13);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](7, "mtd-entry", 14);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](7);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("entry", ctx_r3.modalEntry);
  }
}
class EntryListComponent {
  constructor(dataService) {
    this.dataService = dataService;
    this.edit = false;
    this.entryIDS = [];
    this.isModalOpen = false;
    this.$entriesHash = this.dataService.$entriesHash;
  }
  ngOnInit() {
    this.getEntryIDS();
  }
  getEntryIDS() {
    const entryIDS = [];
    this.entries.forEach(entry => {
      if (entry.entryID) {
        entryIDS.push(entry.entryID);
      }
    });
    this.entryIDS = entryIDS;
  }
  showModal(entry) {
    this.modalEntry = entry;
    this.isModalOpen = true;
  }
  setOpen(value) {
    this.isModalOpen = value;
  }
  didDismiss() {
    this.isModalOpen = false;
  }
  ngOnChanges() {
    this.getEntryIDS();
    if (this.parentEdit !== undefined) {
      this.edit = this.parentEdit;
    }
  }
  trackByFn(index, item) {
    console.log(item);
    console.log(index);
    return item.entryID;
  }
  static #_ = this.ɵfac = function EntryListComponent_Factory(t) {
    return new (t || EntryListComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService));
  };
  static #_2 = this.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdefineComponent"]({
    type: EntryListComponent,
    selectors: [["mtd-entry-list"]],
    inputs: {
      parentEdit: "parentEdit",
      entries: "entries"
    },
    features: [_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵNgOnChangesFeature"]],
    decls: 4,
    vars: 2,
    consts: [[1, "browseElements"], [4, "ngIf"], [3, "didDismiss", "isOpen"], ["class", "matchContainer", "text-wrap", "", 3, "click", 4, "ngFor", "ngForOf"], ["text-wrap", "", 1, "matchContainer", 3, "click"], ["color", "danger", 3, "checked", 4, "ngIf"], [1, "langMatched", "matchLeftContainer"], [1, "langMatched", "response", "browseL1"], [1, "matchRightContainer"], [1, "response", "matchRightDiv"], ["color", "danger", 3, "checked"], ["slot", "end"], [3, "click"], [1, "ion-padding"], [3, "entry"]],
    template: function EntryListComponent_Template(rf, ctx) {
      if (rf & 1) {
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "div", 0);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, EntryListComponent_ion_list_1_Template, 3, 3, "ion-list", 1);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "ion-modal", 2);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("didDismiss", function EntryListComponent_Template_ion_modal_didDismiss_2_listener() {
          return ctx.didDismiss();
        });
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](3, EntryListComponent_ng_template_3_Template, 8, 1, "ng-template");
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      }
      if (rf & 2) {
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.entries.length > 0);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("isOpen", ctx.isModalOpen);
      }
    },
    dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_3__.NgForOf, _angular_common__WEBPACK_IMPORTED_MODULE_3__.NgIf, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonButton, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonButtons, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonCheckbox, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonContent, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonHeader, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonItem, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonLabel, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonList, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonTitle, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonToolbar, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonModal, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.BooleanValueAccessor, _entry_component__WEBPACK_IMPORTED_MODULE_1__.EntryComponent, _angular_common__WEBPACK_IMPORTED_MODULE_3__.AsyncPipe],
    styles: ["/** Ionic CSS Variables **/\n:root {\n  /** primary **/\n  --ion-color-primary: #3880ff;\n  --ion-color-primary-rgb: 56, 128, 255;\n  --ion-color-primary-contrast: #ffffff;\n  --ion-color-primary-contrast-rgb: 255, 255, 255;\n  --ion-color-primary-shade: #3171e0;\n  --ion-color-primary-tint: #4c8dff;\n  /** secondary **/\n  --ion-color-secondary: #3dc2ff;\n  --ion-color-secondary-rgb: 61, 194, 255;\n  --ion-color-secondary-contrast: #ffffff;\n  --ion-color-secondary-contrast-rgb: 255, 255, 255;\n  --ion-color-secondary-shade: #36abe0;\n  --ion-color-secondary-tint: #50c8ff;\n  /** tertiary **/\n  --ion-color-tertiary: #5260ff;\n  --ion-color-tertiary-rgb: 82, 96, 255;\n  --ion-color-tertiary-contrast: #ffffff;\n  --ion-color-tertiary-contrast-rgb: 255, 255, 255;\n  --ion-color-tertiary-shade: #4854e0;\n  --ion-color-tertiary-tint: #6370ff;\n  /** success **/\n  --ion-color-success: #2dd36f;\n  --ion-color-success-rgb: 45, 211, 111;\n  --ion-color-success-contrast: #ffffff;\n  --ion-color-success-contrast-rgb: 255, 255, 255;\n  --ion-color-success-shade: #28ba62;\n  --ion-color-success-tint: #42d77d;\n  /** warning **/\n  --ion-color-warning: #ffc409;\n  --ion-color-warning-rgb: 255, 196, 9;\n  --ion-color-warning-contrast: #000000;\n  --ion-color-warning-contrast-rgb: 0, 0, 0;\n  --ion-color-warning-shade: #e0ac08;\n  --ion-color-warning-tint: #ffca22;\n  /** danger **/\n  --ion-color-danger: #eb445a;\n  --ion-color-danger-rgb: 235, 68, 90;\n  --ion-color-danger-contrast: #ffffff;\n  --ion-color-danger-contrast-rgb: 255, 255, 255;\n  --ion-color-danger-shade: #cf3c4f;\n  --ion-color-danger-tint: #ed576b;\n  /** dark **/\n  --ion-color-dark: #222428;\n  --ion-color-dark-rgb: 34, 36, 40;\n  --ion-color-dark-contrast: #ffffff;\n  --ion-color-dark-contrast-rgb: 255, 255, 255;\n  --ion-color-dark-shade: #1e2023;\n  --ion-color-dark-tint: #383a3e;\n  /** medium **/\n  --ion-color-medium: #92949c;\n  --ion-color-medium-rgb: 146, 148, 156;\n  --ion-color-medium-contrast: #ffffff;\n  --ion-color-medium-contrast-rgb: 255, 255, 255;\n  --ion-color-medium-shade: #808289;\n  --ion-color-medium-tint: #9d9fa6;\n  /** light **/\n  --ion-color-light: #f4f5f8;\n  --ion-color-light-rgb: 244, 245, 248;\n  --ion-color-light-contrast: #000000;\n  --ion-color-light-contrast-rgb: 0, 0, 0;\n  --ion-color-light-shade: #d7d8da;\n  --ion-color-light-tint: #f5f6f9;\n}\n\n@media (prefers-color-scheme: dark) {\n  /*\n   * Dark Colors\n   * -------------------------------------------\n   */\n  body {\n    --ion-color-primary: #428cff;\n    --ion-color-primary-rgb: 66, 140, 255;\n    --ion-color-primary-contrast: #ffffff;\n    --ion-color-primary-contrast-rgb: 255, 255, 255;\n    --ion-color-primary-shade: #3a7be0;\n    --ion-color-primary-tint: #5598ff;\n    --ion-color-secondary: #50c8ff;\n    --ion-color-secondary-rgb: 80, 200, 255;\n    --ion-color-secondary-contrast: #ffffff;\n    --ion-color-secondary-contrast-rgb: 255, 255, 255;\n    --ion-color-secondary-shade: #46b0e0;\n    --ion-color-secondary-tint: #62ceff;\n    --ion-color-tertiary: #6a64ff;\n    --ion-color-tertiary-rgb: 106, 100, 255;\n    --ion-color-tertiary-contrast: #ffffff;\n    --ion-color-tertiary-contrast-rgb: 255, 255, 255;\n    --ion-color-tertiary-shade: #5d58e0;\n    --ion-color-tertiary-tint: #7974ff;\n    --ion-color-success: #2fdf75;\n    --ion-color-success-rgb: 47, 223, 117;\n    --ion-color-success-contrast: #000000;\n    --ion-color-success-contrast-rgb: 0, 0, 0;\n    --ion-color-success-shade: #29c467;\n    --ion-color-success-tint: #44e283;\n    --ion-color-warning: #ffd534;\n    --ion-color-warning-rgb: 255, 213, 52;\n    --ion-color-warning-contrast: #000000;\n    --ion-color-warning-contrast-rgb: 0, 0, 0;\n    --ion-color-warning-shade: #e0bb2e;\n    --ion-color-warning-tint: #ffd948;\n    --ion-color-danger: #ff4961;\n    --ion-color-danger-rgb: 255, 73, 97;\n    --ion-color-danger-contrast: #ffffff;\n    --ion-color-danger-contrast-rgb: 255, 255, 255;\n    --ion-color-danger-shade: #e04055;\n    --ion-color-danger-tint: #ff5b71;\n    --ion-color-dark: #f4f5f8;\n    --ion-color-dark-rgb: 244, 245, 248;\n    --ion-color-dark-contrast: #000000;\n    --ion-color-dark-contrast-rgb: 0, 0, 0;\n    --ion-color-dark-shade: #d7d8da;\n    --ion-color-dark-tint: #f5f6f9;\n    --ion-color-medium: #989aa2;\n    --ion-color-medium-rgb: 152, 154, 162;\n    --ion-color-medium-contrast: #000000;\n    --ion-color-medium-contrast-rgb: 0, 0, 0;\n    --ion-color-medium-shade: #86888f;\n    --ion-color-medium-tint: #a2a4ab;\n    --ion-color-light: #222428;\n    --ion-color-light-rgb: 34, 36, 40;\n    --ion-color-light-contrast: #ffffff;\n    --ion-color-light-contrast-rgb: 255, 255, 255;\n    --ion-color-light-shade: #1e2023;\n    --ion-color-light-tint: #383a3e;\n  }\n  /*\n   * iOS Dark Theme\n   * -------------------------------------------\n   */\n  .ios body {\n    --ion-background-color: #000000;\n    --ion-background-color-rgb: 0, 0, 0;\n    --ion-text-color: #ffffff;\n    --ion-text-color-rgb: 255, 255, 255;\n    --ion-color-step-50: #0d0d0d;\n    --ion-color-step-100: #1a1a1a;\n    --ion-color-step-150: #262626;\n    --ion-color-step-200: #333333;\n    --ion-color-step-250: #404040;\n    --ion-color-step-300: #4d4d4d;\n    --ion-color-step-350: #595959;\n    --ion-color-step-400: #666666;\n    --ion-color-step-450: #737373;\n    --ion-color-step-500: #808080;\n    --ion-color-step-550: #8c8c8c;\n    --ion-color-step-600: #999999;\n    --ion-color-step-650: #a6a6a6;\n    --ion-color-step-700: #b3b3b3;\n    --ion-color-step-750: #bfbfbf;\n    --ion-color-step-800: #cccccc;\n    --ion-color-step-850: #d9d9d9;\n    --ion-color-step-900: #e6e6e6;\n    --ion-color-step-950: #f2f2f2;\n    --ion-item-background: #000000;\n    --ion-card-background: #1c1c1d;\n  }\n  .ios ion-modal {\n    --ion-background-color: var(--ion-color-step-100);\n    --ion-toolbar-background: var(--ion-color-step-150);\n    --ion-toolbar-border-color: var(--ion-color-step-250);\n  }\n  /*\n   * Material Design Dark Theme\n   * -------------------------------------------\n   */\n  .md body {\n    --ion-background-color: #121212;\n    --ion-background-color-rgb: 18, 18, 18;\n    --ion-text-color: #ffffff;\n    --ion-text-color-rgb: 255, 255, 255;\n    --ion-border-color: #222222;\n    --ion-color-step-50: #1e1e1e;\n    --ion-color-step-100: #2a2a2a;\n    --ion-color-step-150: #363636;\n    --ion-color-step-200: #414141;\n    --ion-color-step-250: #4d4d4d;\n    --ion-color-step-300: #595959;\n    --ion-color-step-350: #656565;\n    --ion-color-step-400: #717171;\n    --ion-color-step-450: #7d7d7d;\n    --ion-color-step-500: #898989;\n    --ion-color-step-550: #949494;\n    --ion-color-step-600: #a0a0a0;\n    --ion-color-step-650: #acacac;\n    --ion-color-step-700: #b8b8b8;\n    --ion-color-step-750: #c4c4c4;\n    --ion-color-step-800: #d0d0d0;\n    --ion-color-step-850: #dbdbdb;\n    --ion-color-step-900: #e7e7e7;\n    --ion-color-step-950: #f3f3f3;\n    --ion-item-background: #1e1e1e;\n    --ion-toolbar-background: #1f1f1f;\n    --ion-tab-bar-background: #1f1f1f;\n    --ion-card-background: #1e1e1e;\n  }\n}\n.browseElements {\n  margin: auto;\n  height: auto;\n  width: auto;\n  text-align: center;\n  background-color: var(--ion-color-medium);\n}\n\n.browseElements {\n  margin: auto;\n  height: auto;\n  width: auto;\n  text-align: center !important;\n  background-color: var(--ion-color-medium);\n}\n\n.matchContainer {\n  margin: 1em 0;\n  text-align: center;\n}\n\n.matchLeftDiv {\n  margin-right: 0.2em;\n  text-align: left;\n}\n\n.matchLeftContainer,\n.matchRightContainer {\n  display: initial;\n}\n\n.matchRightDiv {\n  margin-left: 0.2em;\n}\n\n.matchResponse {\n  margin: 2.5em 0 0.75em 0;\n  text-decoration: underline;\n}\n\n.browseL1 {\n  color: var(--ion-color-secondary);\n}\n\n.matchLeftDiv .langMatched {\n  color: var(--ion-color-secondary);\n  font-weight: 900;\n}\n\n.matchRightDiv .langMatched {\n  color: var(--ion-color-secondary);\n  font-weight: 900;\n}\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3BhY2thZ2VzL210ZC1tb2JpbGUtdWkvc3JjL3RoZW1lL3ZhcmlhYmxlcy5zY3NzIiwid2VicGFjazovLy4vcGFja2FnZXMvbXRkLW1vYmlsZS11aS9zcmMvYXBwL3NoYXJlZC9lbnRyeS1saXN0LmNvbXBvbmVudC5zY3NzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUdBLDBCQUFBO0FBQ0E7RUFDRSxjQUFBO0VBQ0EsNEJBQUE7RUFDQSxxQ0FBQTtFQUNBLHFDQUFBO0VBQ0EsK0NBQUE7RUFDQSxrQ0FBQTtFQUNBLGlDQUFBO0VBRUEsZ0JBQUE7RUFDQSw4QkFBQTtFQUNBLHVDQUFBO0VBQ0EsdUNBQUE7RUFDQSxpREFBQTtFQUNBLG9DQUFBO0VBQ0EsbUNBQUE7RUFFQSxlQUFBO0VBQ0EsNkJBQUE7RUFDQSxxQ0FBQTtFQUNBLHNDQUFBO0VBQ0EsZ0RBQUE7RUFDQSxtQ0FBQTtFQUNBLGtDQUFBO0VBRUEsY0FBQTtFQUNBLDRCQUFBO0VBQ0EscUNBQUE7RUFDQSxxQ0FBQTtFQUNBLCtDQUFBO0VBQ0Esa0NBQUE7RUFDQSxpQ0FBQTtFQUVBLGNBQUE7RUFDQSw0QkFBQTtFQUNBLG9DQUFBO0VBQ0EscUNBQUE7RUFDQSx5Q0FBQTtFQUNBLGtDQUFBO0VBQ0EsaUNBQUE7RUFFQSxhQUFBO0VBQ0EsMkJBQUE7RUFDQSxtQ0FBQTtFQUNBLG9DQUFBO0VBQ0EsOENBQUE7RUFDQSxpQ0FBQTtFQUNBLGdDQUFBO0VBRUEsV0FBQTtFQUNBLHlCQUFBO0VBQ0EsZ0NBQUE7RUFDQSxrQ0FBQTtFQUNBLDRDQUFBO0VBQ0EsK0JBQUE7RUFDQSw4QkFBQTtFQUVBLGFBQUE7RUFDQSwyQkFBQTtFQUNBLHFDQUFBO0VBQ0Esb0NBQUE7RUFDQSw4Q0FBQTtFQUNBLGlDQUFBO0VBQ0EsZ0NBQUE7RUFFQSxZQUFBO0VBQ0EsMEJBQUE7RUFDQSxvQ0FBQTtFQUNBLG1DQUFBO0VBQ0EsdUNBQUE7RUFDQSxnQ0FBQTtFQUNBLCtCQUFBO0FDVkY7O0FEYUE7RUFDRTs7O0lBQUE7RUFLQTtJQUNFLDRCQUFBO0lBQ0EscUNBQUE7SUFDQSxxQ0FBQTtJQUNBLCtDQUFBO0lBQ0Esa0NBQUE7SUFDQSxpQ0FBQTtJQUVBLDhCQUFBO0lBQ0EsdUNBQUE7SUFDQSx1Q0FBQTtJQUNBLGlEQUFBO0lBQ0Esb0NBQUE7SUFDQSxtQ0FBQTtJQUVBLDZCQUFBO0lBQ0EsdUNBQUE7SUFDQSxzQ0FBQTtJQUNBLGdEQUFBO0lBQ0EsbUNBQUE7SUFDQSxrQ0FBQTtJQUVBLDRCQUFBO0lBQ0EscUNBQUE7SUFDQSxxQ0FBQTtJQUNBLHlDQUFBO0lBQ0Esa0NBQUE7SUFDQSxpQ0FBQTtJQUVBLDRCQUFBO0lBQ0EscUNBQUE7SUFDQSxxQ0FBQTtJQUNBLHlDQUFBO0lBQ0Esa0NBQUE7SUFDQSxpQ0FBQTtJQUVBLDJCQUFBO0lBQ0EsbUNBQUE7SUFDQSxvQ0FBQTtJQUNBLDhDQUFBO0lBQ0EsaUNBQUE7SUFDQSxnQ0FBQTtJQUVBLHlCQUFBO0lBQ0EsbUNBQUE7SUFDQSxrQ0FBQTtJQUNBLHNDQUFBO0lBQ0EsK0JBQUE7SUFDQSw4QkFBQTtJQUVBLDJCQUFBO0lBQ0EscUNBQUE7SUFDQSxvQ0FBQTtJQUNBLHdDQUFBO0lBQ0EsaUNBQUE7SUFDQSxnQ0FBQTtJQUVBLDBCQUFBO0lBQ0EsaUNBQUE7SUFDQSxtQ0FBQTtJQUNBLDZDQUFBO0lBQ0EsZ0NBQUE7SUFDQSwrQkFBQTtFQ25CRjtFRHNCQTs7O0lBQUE7RUFLQTtJQUNFLCtCQUFBO0lBQ0EsbUNBQUE7SUFFQSx5QkFBQTtJQUNBLG1DQUFBO0lBRUEsNEJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFFQSw4QkFBQTtJQUVBLDhCQUFBO0VDekJGO0VENEJBO0lBQ0UsaURBQUE7SUFDQSxtREFBQTtJQUNBLHFEQUFBO0VDMUJGO0VENkJBOzs7SUFBQTtFQUtBO0lBQ0UsK0JBQUE7SUFDQSxzQ0FBQTtJQUVBLHlCQUFBO0lBQ0EsbUNBQUE7SUFFQSwyQkFBQTtJQUVBLDRCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBRUEsOEJBQUE7SUFFQSxpQ0FBQTtJQUVBLGlDQUFBO0lBRUEsOEJBQUE7RUNuQ0Y7QUFDRjtBQXBNQTtFQUNFLFlBQUE7RUFDQSxZQUFBO0VBQ0EsV0FBQTtFQUNBLGtCQUFBO0VBQ0EseUNBQUE7QUFzTUY7O0FBbk1BO0VBQ0UsWUFBQTtFQUNBLFlBQUE7RUFDQSxXQUFBO0VBQ0EsNkJBQUE7RUFDQSx5Q0FBQTtBQXNNRjs7QUFuTUE7RUFDRSxhQUFBO0VBQ0Esa0JBQUE7QUFzTUY7O0FBbk1BO0VBQ0UsbUJBQUE7RUFDQSxnQkFBQTtBQXNNRjs7QUFuTUE7O0VBRUUsZ0JBQUE7QUFzTUY7O0FBbk1BO0VBQ0Usa0JBQUE7QUFzTUY7O0FBbk1BO0VBQ0Usd0JBQUE7RUFDQSwwQkFBQTtBQXNNRjs7QUFuTUE7RUFDRSxpQ0FBQTtBQXNNRjs7QUFuTUE7RUFDRSxpQ0FBQTtFQUVBLGdCQUFBO0FBcU1GOztBQWpNQTtFQUNFLGlDQUFBO0VBQ0EsZ0JBQUE7QUFvTUYiLCJzb3VyY2VzQ29udGVudCI6WyIvLyBJb25pYyBWYXJpYWJsZXMgYW5kIFRoZW1pbmcuIEZvciBtb3JlIGluZm8sIHBsZWFzZSBzZWU6XG4vLyBodHRwOi8vaW9uaWNmcmFtZXdvcmsuY29tL2RvY3MvdGhlbWluZy9cblxuLyoqIElvbmljIENTUyBWYXJpYWJsZXMgKiovXG46cm9vdCB7XG4gIC8qKiBwcmltYXJ5ICoqL1xuICAtLWlvbi1jb2xvci1wcmltYXJ5OiAjMzg4MGZmO1xuICAtLWlvbi1jb2xvci1wcmltYXJ5LXJnYjogNTYsIDEyOCwgMjU1O1xuICAtLWlvbi1jb2xvci1wcmltYXJ5LWNvbnRyYXN0OiAjZmZmZmZmO1xuICAtLWlvbi1jb2xvci1wcmltYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgLS1pb24tY29sb3ItcHJpbWFyeS1zaGFkZTogIzMxNzFlMDtcbiAgLS1pb24tY29sb3ItcHJpbWFyeS10aW50OiAjNGM4ZGZmO1xuXG4gIC8qKiBzZWNvbmRhcnkgKiovXG4gIC0taW9uLWNvbG9yLXNlY29uZGFyeTogIzNkYzJmZjtcbiAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LXJnYjogNjEsIDE5NCwgMjU1O1xuICAtLWlvbi1jb2xvci1zZWNvbmRhcnktY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLXNlY29uZGFyeS1jb250cmFzdC1yZ2I6IDI1NSwgMjU1LCAyNTU7XG4gIC0taW9uLWNvbG9yLXNlY29uZGFyeS1zaGFkZTogIzM2YWJlMDtcbiAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LXRpbnQ6ICM1MGM4ZmY7XG5cbiAgLyoqIHRlcnRpYXJ5ICoqL1xuICAtLWlvbi1jb2xvci10ZXJ0aWFyeTogIzUyNjBmZjtcbiAgLS1pb24tY29sb3ItdGVydGlhcnktcmdiOiA4MiwgOTYsIDI1NTtcbiAgLS1pb24tY29sb3ItdGVydGlhcnktY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLXRlcnRpYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgLS1pb24tY29sb3ItdGVydGlhcnktc2hhZGU6ICM0ODU0ZTA7XG4gIC0taW9uLWNvbG9yLXRlcnRpYXJ5LXRpbnQ6ICM2MzcwZmY7XG5cbiAgLyoqIHN1Y2Nlc3MgKiovXG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3M6ICMyZGQzNmY7XG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3MtcmdiOiA0NSwgMjExLCAxMTE7XG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3MtY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3MtY29udHJhc3QtcmdiOiAyNTUsIDI1NSwgMjU1O1xuICAtLWlvbi1jb2xvci1zdWNjZXNzLXNoYWRlOiAjMjhiYTYyO1xuICAtLWlvbi1jb2xvci1zdWNjZXNzLXRpbnQ6ICM0MmQ3N2Q7XG5cbiAgLyoqIHdhcm5pbmcgKiovXG4gIC0taW9uLWNvbG9yLXdhcm5pbmc6ICNmZmM0MDk7XG4gIC0taW9uLWNvbG9yLXdhcm5pbmctcmdiOiAyNTUsIDE5NiwgOTtcbiAgLS1pb24tY29sb3Itd2FybmluZy1jb250cmFzdDogIzAwMDAwMDtcbiAgLS1pb24tY29sb3Itd2FybmluZy1jb250cmFzdC1yZ2I6IDAsIDAsIDA7XG4gIC0taW9uLWNvbG9yLXdhcm5pbmctc2hhZGU6ICNlMGFjMDg7XG4gIC0taW9uLWNvbG9yLXdhcm5pbmctdGludDogI2ZmY2EyMjtcblxuICAvKiogZGFuZ2VyICoqL1xuICAtLWlvbi1jb2xvci1kYW5nZXI6ICNlYjQ0NWE7XG4gIC0taW9uLWNvbG9yLWRhbmdlci1yZ2I6IDIzNSwgNjgsIDkwO1xuICAtLWlvbi1jb2xvci1kYW5nZXItY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLWRhbmdlci1jb250cmFzdC1yZ2I6IDI1NSwgMjU1LCAyNTU7XG4gIC0taW9uLWNvbG9yLWRhbmdlci1zaGFkZTogI2NmM2M0ZjtcbiAgLS1pb24tY29sb3ItZGFuZ2VyLXRpbnQ6ICNlZDU3NmI7XG5cbiAgLyoqIGRhcmsgKiovXG4gIC0taW9uLWNvbG9yLWRhcms6ICMyMjI0Mjg7XG4gIC0taW9uLWNvbG9yLWRhcmstcmdiOiAzNCwgMzYsIDQwO1xuICAtLWlvbi1jb2xvci1kYXJrLWNvbnRyYXN0OiAjZmZmZmZmO1xuICAtLWlvbi1jb2xvci1kYXJrLWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgLS1pb24tY29sb3ItZGFyay1zaGFkZTogIzFlMjAyMztcbiAgLS1pb24tY29sb3ItZGFyay10aW50OiAjMzgzYTNlO1xuXG4gIC8qKiBtZWRpdW0gKiovXG4gIC0taW9uLWNvbG9yLW1lZGl1bTogIzkyOTQ5YztcbiAgLS1pb24tY29sb3ItbWVkaXVtLXJnYjogMTQ2LCAxNDgsIDE1NjtcbiAgLS1pb24tY29sb3ItbWVkaXVtLWNvbnRyYXN0OiAjZmZmZmZmO1xuICAtLWlvbi1jb2xvci1tZWRpdW0tY29udHJhc3QtcmdiOiAyNTUsIDI1NSwgMjU1O1xuICAtLWlvbi1jb2xvci1tZWRpdW0tc2hhZGU6ICM4MDgyODk7XG4gIC0taW9uLWNvbG9yLW1lZGl1bS10aW50OiAjOWQ5ZmE2O1xuXG4gIC8qKiBsaWdodCAqKi9cbiAgLS1pb24tY29sb3ItbGlnaHQ6ICNmNGY1Zjg7XG4gIC0taW9uLWNvbG9yLWxpZ2h0LXJnYjogMjQ0LCAyNDUsIDI0ODtcbiAgLS1pb24tY29sb3ItbGlnaHQtY29udHJhc3Q6ICMwMDAwMDA7XG4gIC0taW9uLWNvbG9yLWxpZ2h0LWNvbnRyYXN0LXJnYjogMCwgMCwgMDtcbiAgLS1pb24tY29sb3ItbGlnaHQtc2hhZGU6ICNkN2Q4ZGE7XG4gIC0taW9uLWNvbG9yLWxpZ2h0LXRpbnQ6ICNmNWY2Zjk7XG59XG5cbkBtZWRpYSAocHJlZmVycy1jb2xvci1zY2hlbWU6IGRhcmspIHtcbiAgLypcbiAgICogRGFyayBDb2xvcnNcbiAgICogLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxuICAgKi9cblxuICBib2R5IHtcbiAgICAtLWlvbi1jb2xvci1wcmltYXJ5OiAjNDI4Y2ZmO1xuICAgIC0taW9uLWNvbG9yLXByaW1hcnktcmdiOiA2NiwgMTQwLCAyNTU7XG4gICAgLS1pb24tY29sb3ItcHJpbWFyeS1jb250cmFzdDogI2ZmZmZmZjtcbiAgICAtLWlvbi1jb2xvci1wcmltYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgICAtLWlvbi1jb2xvci1wcmltYXJ5LXNoYWRlOiAjM2E3YmUwO1xuICAgIC0taW9uLWNvbG9yLXByaW1hcnktdGludDogIzU1OThmZjtcblxuICAgIC0taW9uLWNvbG9yLXNlY29uZGFyeTogIzUwYzhmZjtcbiAgICAtLWlvbi1jb2xvci1zZWNvbmRhcnktcmdiOiA4MCwgMjAwLCAyNTU7XG4gICAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LWNvbnRyYXN0OiAjZmZmZmZmO1xuICAgIC0taW9uLWNvbG9yLXNlY29uZGFyeS1jb250cmFzdC1yZ2I6IDI1NSwgMjU1LCAyNTU7XG4gICAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LXNoYWRlOiAjNDZiMGUwO1xuICAgIC0taW9uLWNvbG9yLXNlY29uZGFyeS10aW50OiAjNjJjZWZmO1xuXG4gICAgLS1pb24tY29sb3ItdGVydGlhcnk6ICM2YTY0ZmY7XG4gICAgLS1pb24tY29sb3ItdGVydGlhcnktcmdiOiAxMDYsIDEwMCwgMjU1O1xuICAgIC0taW9uLWNvbG9yLXRlcnRpYXJ5LWNvbnRyYXN0OiAjZmZmZmZmO1xuICAgIC0taW9uLWNvbG9yLXRlcnRpYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgICAtLWlvbi1jb2xvci10ZXJ0aWFyeS1zaGFkZTogIzVkNThlMDtcbiAgICAtLWlvbi1jb2xvci10ZXJ0aWFyeS10aW50OiAjNzk3NGZmO1xuXG4gICAgLS1pb24tY29sb3Itc3VjY2VzczogIzJmZGY3NTtcbiAgICAtLWlvbi1jb2xvci1zdWNjZXNzLXJnYjogNDcsIDIyMywgMTE3O1xuICAgIC0taW9uLWNvbG9yLXN1Y2Nlc3MtY29udHJhc3Q6ICMwMDAwMDA7XG4gICAgLS1pb24tY29sb3Itc3VjY2Vzcy1jb250cmFzdC1yZ2I6IDAsIDAsIDA7XG4gICAgLS1pb24tY29sb3Itc3VjY2Vzcy1zaGFkZTogIzI5YzQ2NztcbiAgICAtLWlvbi1jb2xvci1zdWNjZXNzLXRpbnQ6ICM0NGUyODM7XG5cbiAgICAtLWlvbi1jb2xvci13YXJuaW5nOiAjZmZkNTM0O1xuICAgIC0taW9uLWNvbG9yLXdhcm5pbmctcmdiOiAyNTUsIDIxMywgNTI7XG4gICAgLS1pb24tY29sb3Itd2FybmluZy1jb250cmFzdDogIzAwMDAwMDtcbiAgICAtLWlvbi1jb2xvci13YXJuaW5nLWNvbnRyYXN0LXJnYjogMCwgMCwgMDtcbiAgICAtLWlvbi1jb2xvci13YXJuaW5nLXNoYWRlOiAjZTBiYjJlO1xuICAgIC0taW9uLWNvbG9yLXdhcm5pbmctdGludDogI2ZmZDk0ODtcblxuICAgIC0taW9uLWNvbG9yLWRhbmdlcjogI2ZmNDk2MTtcbiAgICAtLWlvbi1jb2xvci1kYW5nZXItcmdiOiAyNTUsIDczLCA5NztcbiAgICAtLWlvbi1jb2xvci1kYW5nZXItY29udHJhc3Q6ICNmZmZmZmY7XG4gICAgLS1pb24tY29sb3ItZGFuZ2VyLWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgICAtLWlvbi1jb2xvci1kYW5nZXItc2hhZGU6ICNlMDQwNTU7XG4gICAgLS1pb24tY29sb3ItZGFuZ2VyLXRpbnQ6ICNmZjViNzE7XG5cbiAgICAtLWlvbi1jb2xvci1kYXJrOiAjZjRmNWY4O1xuICAgIC0taW9uLWNvbG9yLWRhcmstcmdiOiAyNDQsIDI0NSwgMjQ4O1xuICAgIC0taW9uLWNvbG9yLWRhcmstY29udHJhc3Q6ICMwMDAwMDA7XG4gICAgLS1pb24tY29sb3ItZGFyay1jb250cmFzdC1yZ2I6IDAsIDAsIDA7XG4gICAgLS1pb24tY29sb3ItZGFyay1zaGFkZTogI2Q3ZDhkYTtcbiAgICAtLWlvbi1jb2xvci1kYXJrLXRpbnQ6ICNmNWY2Zjk7XG5cbiAgICAtLWlvbi1jb2xvci1tZWRpdW06ICM5ODlhYTI7XG4gICAgLS1pb24tY29sb3ItbWVkaXVtLXJnYjogMTUyLCAxNTQsIDE2MjtcbiAgICAtLWlvbi1jb2xvci1tZWRpdW0tY29udHJhc3Q6ICMwMDAwMDA7XG4gICAgLS1pb24tY29sb3ItbWVkaXVtLWNvbnRyYXN0LXJnYjogMCwgMCwgMDtcbiAgICAtLWlvbi1jb2xvci1tZWRpdW0tc2hhZGU6ICM4Njg4OGY7XG4gICAgLS1pb24tY29sb3ItbWVkaXVtLXRpbnQ6ICNhMmE0YWI7XG5cbiAgICAtLWlvbi1jb2xvci1saWdodDogIzIyMjQyODtcbiAgICAtLWlvbi1jb2xvci1saWdodC1yZ2I6IDM0LCAzNiwgNDA7XG4gICAgLS1pb24tY29sb3ItbGlnaHQtY29udHJhc3Q6ICNmZmZmZmY7XG4gICAgLS1pb24tY29sb3ItbGlnaHQtY29udHJhc3QtcmdiOiAyNTUsIDI1NSwgMjU1O1xuICAgIC0taW9uLWNvbG9yLWxpZ2h0LXNoYWRlOiAjMWUyMDIzO1xuICAgIC0taW9uLWNvbG9yLWxpZ2h0LXRpbnQ6ICMzODNhM2U7XG4gIH1cblxuICAvKlxuICAgKiBpT1MgRGFyayBUaGVtZVxuICAgKiAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG4gICAqL1xuXG4gIC5pb3MgYm9keSB7XG4gICAgLS1pb24tYmFja2dyb3VuZC1jb2xvcjogIzAwMDAwMDtcbiAgICAtLWlvbi1iYWNrZ3JvdW5kLWNvbG9yLXJnYjogMCwgMCwgMDtcblxuICAgIC0taW9uLXRleHQtY29sb3I6ICNmZmZmZmY7XG4gICAgLS1pb24tdGV4dC1jb2xvci1yZ2I6IDI1NSwgMjU1LCAyNTU7XG5cbiAgICAtLWlvbi1jb2xvci1zdGVwLTUwOiAjMGQwZDBkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTAwOiAjMWExYTFhO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTUwOiAjMjYyNjI2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjAwOiAjMzMzMzMzO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjUwOiAjNDA0MDQwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzAwOiAjNGQ0ZDRkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzUwOiAjNTk1OTU5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDAwOiAjNjY2NjY2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDUwOiAjNzM3MzczO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTAwOiAjODA4MDgwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTUwOiAjOGM4YzhjO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjAwOiAjOTk5OTk5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjUwOiAjYTZhNmE2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzAwOiAjYjNiM2IzO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzUwOiAjYmZiZmJmO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODAwOiAjY2NjY2NjO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODUwOiAjZDlkOWQ5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTAwOiAjZTZlNmU2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTUwOiAjZjJmMmYyO1xuXG4gICAgLS1pb24taXRlbS1iYWNrZ3JvdW5kOiAjMDAwMDAwO1xuXG4gICAgLS1pb24tY2FyZC1iYWNrZ3JvdW5kOiAjMWMxYzFkO1xuICB9XG5cbiAgLmlvcyBpb24tbW9kYWwge1xuICAgIC0taW9uLWJhY2tncm91bmQtY29sb3I6IHZhcigtLWlvbi1jb2xvci1zdGVwLTEwMCk7XG4gICAgLS1pb24tdG9vbGJhci1iYWNrZ3JvdW5kOiB2YXIoLS1pb24tY29sb3Itc3RlcC0xNTApO1xuICAgIC0taW9uLXRvb2xiYXItYm9yZGVyLWNvbG9yOiB2YXIoLS1pb24tY29sb3Itc3RlcC0yNTApO1xuICB9XG5cbiAgLypcbiAgICogTWF0ZXJpYWwgRGVzaWduIERhcmsgVGhlbWVcbiAgICogLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxuICAgKi9cblxuICAubWQgYm9keSB7XG4gICAgLS1pb24tYmFja2dyb3VuZC1jb2xvcjogIzEyMTIxMjtcbiAgICAtLWlvbi1iYWNrZ3JvdW5kLWNvbG9yLXJnYjogMTgsIDE4LCAxODtcblxuICAgIC0taW9uLXRleHQtY29sb3I6ICNmZmZmZmY7XG4gICAgLS1pb24tdGV4dC1jb2xvci1yZ2I6IDI1NSwgMjU1LCAyNTU7XG5cbiAgICAtLWlvbi1ib3JkZXItY29sb3I6ICMyMjIyMjI7XG5cbiAgICAtLWlvbi1jb2xvci1zdGVwLTUwOiAjMWUxZTFlO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTAwOiAjMmEyYTJhO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTUwOiAjMzYzNjM2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjAwOiAjNDE0MTQxO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjUwOiAjNGQ0ZDRkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzAwOiAjNTk1OTU5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzUwOiAjNjU2NTY1O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDAwOiAjNzE3MTcxO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDUwOiAjN2Q3ZDdkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTAwOiAjODk4OTg5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTUwOiAjOTQ5NDk0O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjAwOiAjYTBhMGEwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjUwOiAjYWNhY2FjO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzAwOiAjYjhiOGI4O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzUwOiAjYzRjNGM0O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODAwOiAjZDBkMGQwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODUwOiAjZGJkYmRiO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTAwOiAjZTdlN2U3O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTUwOiAjZjNmM2YzO1xuXG4gICAgLS1pb24taXRlbS1iYWNrZ3JvdW5kOiAjMWUxZTFlO1xuXG4gICAgLS1pb24tdG9vbGJhci1iYWNrZ3JvdW5kOiAjMWYxZjFmO1xuXG4gICAgLS1pb24tdGFiLWJhci1iYWNrZ3JvdW5kOiAjMWYxZjFmO1xuXG4gICAgLS1pb24tY2FyZC1iYWNrZ3JvdW5kOiAjMWUxZTFlO1xuICB9XG59XG4iLCJAaW1wb3J0ICcuLi8uLi90aGVtZS92YXJpYWJsZXMuc2Nzcyc7XG4vLyBlbnRyeS1saXN0IHtcbi5icm93c2VFbGVtZW50cyB7XG4gIG1hcmdpbjogYXV0bztcbiAgaGVpZ2h0OiBhdXRvO1xuICB3aWR0aDogYXV0bztcbiAgdGV4dC1hbGlnbjogY2VudGVyO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1pb24tY29sb3ItbWVkaXVtKTtcbn1cblxuLmJyb3dzZUVsZW1lbnRzIHtcbiAgbWFyZ2luOiBhdXRvO1xuICBoZWlnaHQ6IGF1dG87XG4gIHdpZHRoOiBhdXRvO1xuICB0ZXh0LWFsaWduOiBjZW50ZXIgIWltcG9ydGFudDtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0taW9uLWNvbG9yLW1lZGl1bSk7XG59XG5cbi5tYXRjaENvbnRhaW5lciB7XG4gIG1hcmdpbjogMWVtIDA7XG4gIHRleHQtYWxpZ246IGNlbnRlcjtcbn1cblxuLm1hdGNoTGVmdERpdiB7XG4gIG1hcmdpbi1yaWdodDogMC4yZW07XG4gIHRleHQtYWxpZ246IGxlZnQ7XG59XG5cbi5tYXRjaExlZnRDb250YWluZXIsXG4ubWF0Y2hSaWdodENvbnRhaW5lciB7XG4gIGRpc3BsYXk6IGluaXRpYWw7XG59XG5cbi5tYXRjaFJpZ2h0RGl2IHtcbiAgbWFyZ2luLWxlZnQ6IDAuMmVtO1xufVxuXG4ubWF0Y2hSZXNwb25zZSB7XG4gIG1hcmdpbjogMi41ZW0gMCAwLjc1ZW0gMDtcbiAgdGV4dC1kZWNvcmF0aW9uOiB1bmRlcmxpbmU7XG59XG5cbi5icm93c2VMMSB7XG4gIGNvbG9yOiB2YXIoLS1pb24tY29sb3Itc2Vjb25kYXJ5KTtcbn1cblxuLm1hdGNoTGVmdERpdiAubGFuZ01hdGNoZWQge1xuICBjb2xvcjogdmFyKC0taW9uLWNvbG9yLXNlY29uZGFyeSk7XG4gIC8vIGJvcmRlci1yYWRpdXM6IDE1cHg7XG4gIGZvbnQtd2VpZ2h0OiA5MDA7XG4gIC8vIHBhZGRpbmc6IDVweDtcbn1cblxuLm1hdGNoUmlnaHREaXYgLmxhbmdNYXRjaGVkIHtcbiAgY29sb3I6IHZhcigtLWlvbi1jb2xvci1zZWNvbmRhcnkpO1xuICBmb250LXdlaWdodDogOTAwO1xufVxuXG4vLyBpb24taXRlbSB7XG4vLyAgICAgdGV4dC1hbGlnbjogY2VudGVyO1xuLy8gfVxuLy8gfVxuIl0sInNvdXJjZVJvb3QiOiIifQ== */"],
    encapsulation: 2
  });
}

/***/ }),

/***/ 4247:
/*!******************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/shared/entry.component.ts ***!
  \******************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   EntryComponent: () => (/* binding */ EntryComponent)
/* harmony export */ });
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../data.service */ 5329);
/* harmony import */ var _settings_service__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./settings.service */ 9540);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ 7580);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @ionic/angular */ 1507);







function EntryComponent_img_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](0, "img", 2);
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpropertyInterpolate"]("src", ctx_r0.entry.img, _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵsanitizeUrl"]);
  }
}
function EntryComponent_ion_list_8_ion_item_4_ion_button_1_span_2_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const audio_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2).$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](audio_r3.description);
  }
}
function EntryComponent_ion_list_8_ion_item_4_ion_button_1_span_3_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1, "Play");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
}
function EntryComponent_ion_list_8_ion_item_4_ion_button_1_Template(rf, ctx) {
  if (rf & 1) {
    const _r2 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-button", 6);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function EntryComponent_ion_list_8_ion_item_4_ion_button_1_Template_ion_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r2);
      const audio_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().$implicit;
      const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r0.playAudio(audio_r3));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](1, "ion-icon", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](2, EntryComponent_ion_list_8_ion_item_4_ion_button_1_span_2_Template, 2, 1, "span", 1)(3, EntryComponent_ion_list_8_ion_item_4_ion_button_1_span_3_Template, 2, 0, "span", 1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const audio_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", audio_r3.description && audio_r3.description !== "null");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", !audio_r3.description || audio_r3.description === "null");
  }
}
function EntryComponent_ion_list_8_ion_item_4_ion_button_2_Template(rf, ctx) {
  if (rf & 1) {
    const _r4 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-button", 8);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function EntryComponent_ion_list_8_ion_item_4_ion_button_2_Template_ion_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r4);
      const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](3);
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r0.stopAllAudio());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](1, "ion-icon", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3, "Stop");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
}
function EntryComponent_ion_list_8_ion_item_4_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-item");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, EntryComponent_ion_list_8_ion_item_4_ion_button_1_Template, 4, 2, "ion-button", 4)(2, EntryComponent_ion_list_8_ion_item_4_ion_button_2_Template, 4, 0, "ion-button", 5);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const audio_r3 = ctx.$implicit;
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", !ctx_r0.playing && audio_r3.filename);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r0.playing);
  }
}
function EntryComponent_ion_list_8_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-list")(1, "ion-list-header")(2, "ion-label");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3, "Audio");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](4, EntryComponent_ion_list_8_ion_item_4_Template, 3, 2, "ion-item", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngForOf", ctx_r0.entry.audio);
  }
}
function EntryComponent_ion_list_9_ion_item_4_ion_note_3_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-note", 10);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const item_r5 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](item_r5.value);
  }
}
function EntryComponent_ion_list_9_ion_item_4_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-item")(1, "ion-label");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](3, EntryComponent_ion_list_9_ion_item_4_ion_note_3_Template, 2, 1, "ion-note", 9);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const item_r5 = ctx.$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](item_r5.key);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", item_r5.value);
  }
}
function EntryComponent_ion_list_9_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-list")(1, "ion-list-header")(2, "ion-label");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3, "Optional");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](4, EntryComponent_ion_list_9_ion_item_4_Template, 4, 2, "ion-item", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipe"](5, "keyvalue");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngForOf", _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipeBind2"](5, 1, ctx_r0.optionalInfo(ctx_r0.entry.optional), ctx_r0.originalOrder));
  }
}
function EntryComponent_ion_list_11_ion_item_4_ion_button_2_span_2_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const i_r7 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2).index;
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](ctx_r0.entry.example_sentence_audio[i_r7][0].description);
  }
}
function EntryComponent_ion_list_11_ion_item_4_ion_button_2_Template(rf, ctx) {
  if (rf & 1) {
    const _r6 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-button", 6);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function EntryComponent_ion_list_11_ion_item_4_ion_button_2_Template_ion_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r6);
      const i_r7 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().index;
      const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r0.playAudio(ctx_r0.entry.example_sentence_audio[i_r7][0]));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](1, "ion-icon", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](2, EntryComponent_ion_list_11_ion_item_4_ion_button_2_span_2_Template, 2, 1, "span", 1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const i_r7 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().index;
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r0.entry.example_sentence_audio[i_r7][0].description);
  }
}
function EntryComponent_ion_list_11_ion_item_4_span_5_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const i_r7 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().index;
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate1"](" - ", ctx_r0.entry.example_sentence_definition[i_r7], "");
  }
}
function EntryComponent_ion_list_11_ion_item_4_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-item")(1, "ion-thumbnail", 11);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](2, EntryComponent_ion_list_11_ion_item_4_ion_button_2_Template, 3, 1, "ion-button", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](3, "ion-label");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](5, EntryComponent_ion_list_11_ion_item_4_span_5_Template, 2, 1, "span", 1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const sentence_r8 = ctx.$implicit;
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r0.entry.example_sentence_audio && ctx_r0.checkListIsNotEmpty(ctx_r0.entry.example_sentence_audio));
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](sentence_r8);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r0.entry.example_sentence_definition && ctx_r0.checkListIsNotEmpty(ctx_r0.entry.example_sentence_definition));
  }
}
function EntryComponent_ion_list_11_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-list")(1, "ion-list-header")(2, "ion-label");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3, "Example Sentences");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](4, EntryComponent_ion_list_11_ion_item_4_Template, 6, 3, "ion-item", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngForOf", ctx_r0.entry.example_sentence);
  }
}
function EntryComponent_ion_footer_12_Template(rf, ctx) {
  if (rf & 1) {
    const _r9 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-footer")(1, "ion-toolbar", 12)(2, "ion-item")(3, "ion-toggle", 13);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipe"](4, "async");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("ionChange", function EntryComponent_ion_footer_12_Template_ion_toggle_ionChange_3_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r9);
      const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r0.changeOptional());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](5, "Show optional information");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("checked", _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipeBind1"](4, 1, ctx_r0.settingsService.showOptionalInfo$));
  }
}
class EntryComponent {
  constructor(dataService, settingsService) {
    this.dataService = dataService;
    this.settingsService = settingsService;
    this.audio_playing = [];
    this.playing = false;
    this.originalOrder = () => {
      return 0;
    };
    // this.entry.
  }
  ngOnInit() {
    console.log(this.entry);
  }
  ngOnDestroy() {
    this.stopAllAudio();
  }
  changeOptional() {
    this.settingsService.showOptionalInfo$.next(!this.settingsService.showOptionalInfo$.value);
  }
  checkOptional(optional) {
    if (optional) {
      return Object.values(optional).filter(x => x).length > 0;
    } else {
      return false;
    }
  }
  checkListIsNotEmpty(anyList) {
    return anyList.filter(e => e).length > 0;
  }
  optionalInfo(optional) {
    if (optional) {
      return new Map(Object.entries(optional).filter(([_, v]) => v.toString().length));
    } else {
      return {};
    }
  }
  stopAllAudio() {
    this.audio_playing.forEach(element => {
      element.pause();
    });
    this.audio_playing = [];
  }
  playAudio(audio) {
    this.stopAllAudio();
    const audioElement = new Audio(audio.filename);
    audioElement.onerror = err => {
      console.log(err);
      this.audio_playing.pop();
    };
    audioElement.onended = () => {
      this.audio_playing.pop();
      this.playing = false;
    };
    audioElement.onpause = () => {
      this.playing = false;
    };
    audioElement.onplay = () => {
      this.playing = true;
    };
    this.audio_playing.push(audioElement);
    audioElement.play();
  }
  static #_ = this.ɵfac = function EntryComponent_Factory(t) {
    return new (t || EntryComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService), _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_settings_service__WEBPACK_IMPORTED_MODULE_1__.SettingsService));
  };
  static #_2 = this.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdefineComponent"]({
    type: EntryComponent,
    selectors: [["mtd-entry"]],
    inputs: {
      entry: "entry"
    },
    decls: 13,
    vars: 9,
    consts: [["alt", "entry image", 3, "src", 4, "ngIf"], [4, "ngIf"], ["alt", "entry image", 3, "src"], [4, "ngFor", "ngForOf"], [3, "click", 4, "ngIf"], ["color", "danger", 3, "click", 4, "ngIf"], [3, "click"], ["slot", "start", "name", "musical-notes-outline"], ["color", "danger", 3, "click"], ["class", "optional__note", "slot", "end", 4, "ngIf"], ["slot", "end", 1, "optional__note"], ["slot", "start"], [1, "optional"], ["labelPlacement", "start", 3, "ionChange", "checked"]],
    template: function EntryComponent_Template(rf, ctx) {
      if (rf & 1) {
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-card");
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, EntryComponent_img_1_Template, 1, 1, "img", 0);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "ion-card-header")(3, "ion-card-title");
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](5, "ion-card-subtitle");
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](6);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](7, "ion-card-content");
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](8, EntryComponent_ion_list_8_Template, 5, 1, "ion-list", 1)(9, EntryComponent_ion_list_9_Template, 6, 4, "ion-list", 1);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipe"](10, "async");
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](11, EntryComponent_ion_list_11_Template, 5, 1, "ion-list", 1);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](12, EntryComponent_ion_footer_12_Template, 6, 3, "ion-footer", 1);
      }
      if (rf & 2) {
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.entry.img);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](3);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](ctx.entry.word);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate"](ctx.entry.definition);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.entry.audio && ctx.entry.audio.length > 0);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipeBind1"](10, 7, ctx.settingsService.showOptionalInfo$) && ctx.checkOptional(ctx.entry.optional));
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.entry.example_sentence && ctx.checkListIsNotEmpty(ctx.entry.example_sentence));
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.entry.optional && ctx.checkOptional(ctx.entry.optional));
      }
    },
    dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_3__.NgForOf, _angular_common__WEBPACK_IMPORTED_MODULE_3__.NgIf, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonButton, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonCard, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonCardContent, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonCardHeader, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonCardSubtitle, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonCardTitle, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonFooter, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonIcon, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonItem, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonLabel, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonList, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonListHeader, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonNote, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonThumbnail, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonToggle, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonToolbar, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.BooleanValueAccessor, _angular_common__WEBPACK_IMPORTED_MODULE_3__.AsyncPipe, _angular_common__WEBPACK_IMPORTED_MODULE_3__.KeyValuePipe],
    styles: [".optional {\n  bottom: 0;\n  position: fixed;\n  width: 100%;\n  min-width: 100%;\n  left: 0;\n}\n.optional__note {\n  max-width: 70%;\n}\n\nion-note {\n  font-size: inherit;\n}\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3BhY2thZ2VzL210ZC1tb2JpbGUtdWkvc3JjL2FwcC9zaGFyZWQvZW50cnkuY29tcG9uZW50LnNjc3MiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7RUFDRSxTQUFBO0VBQ0EsZUFBQTtFQUNBLFdBQUE7RUFDQSxlQUFBO0VBQ0EsT0FBQTtBQUNGO0FBQ0U7RUFDRSxjQUFBO0FBQ0o7O0FBR0E7RUFDRSxrQkFBQTtBQUFGIiwic291cmNlc0NvbnRlbnQiOlsiLm9wdGlvbmFsIHtcbiAgYm90dG9tOiAwO1xuICBwb3NpdGlvbjogZml4ZWQ7XG4gIHdpZHRoOiAxMDAlO1xuICBtaW4td2lkdGg6IDEwMCU7XG4gIGxlZnQ6IDA7XG5cbiAgJl9fbm90ZSB7XG4gICAgbWF4LXdpZHRoOiA3MCU7XG4gIH1cbn1cblxuaW9uLW5vdGUge1xuICBmb250LXNpemU6IGluaGVyaXQ7XG59XG4iXSwic291cmNlUm9vdCI6IiJ9 */"],
    encapsulation: 2
  });
}

/***/ }),

/***/ 2155:
/*!******************************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/shared/search-entry-list.component.ts ***!
  \******************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SearchEntryListComponent: () => (/* binding */ SearchEntryListComponent)
/* harmony export */ });
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../data.service */ 5329);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ 7580);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _entry_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./entry.component */ 4247);






function SearchEntryListComponent_ion_list_1_div_1_ion_item_1_ion_checkbox_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](0, "ion-checkbox", 10);
  }
  if (rf & 2) {
    const entry_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().$implicit;
    const entriesHash_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().ngIf;
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("checked", entriesHash_r3[entry_r2[1]]["checked"]);
  }
}
function SearchEntryListComponent_ion_list_1_div_1_ion_item_1_Template(rf, ctx) {
  if (rf & 1) {
    const _r1 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-item", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function SearchEntryListComponent_ion_list_1_div_1_ion_item_1_Template_ion_item_click_0_listener() {
      const entry_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r1).$implicit;
      const entriesHash_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]().ngIf;
      const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r3.showModal(entriesHash_r3[entry_r2[1]]));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, SearchEntryListComponent_ion_list_1_div_1_ion_item_1_ion_checkbox_1_Template, 1, 1, "ion-checkbox", 5);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "ion-label")(3, "div", 6);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](4, "span", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](5, "div", 6)(6, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](7, " | ");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](8, "div", 8);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](9, "span", 9);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()();
  }
  if (rf & 2) {
    const entry_r2 = ctx.$implicit;
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r3.edit);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("innerHTML", ctx_r3.highlight(entry_r2, "L1"), _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵsanitizeHtml"]);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](5);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("innerHTML", ctx_r3.highlight(entry_r2, "L2"), _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵsanitizeHtml"]);
  }
}
function SearchEntryListComponent_ion_list_1_div_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "div");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, SearchEntryListComponent_ion_list_1_div_1_ion_item_1_Template, 10, 3, "ion-item", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngForOf", ctx_r3.entries.slice(0, ctx_r3.maxResults));
  }
}
function SearchEntryListComponent_ion_list_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-list");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, SearchEntryListComponent_ion_list_1_div_1_Template, 2, 1, "div", 1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipe"](2, "async");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpipeBind1"](2, 1, ctx_r3.$entriesHash));
  }
}
function SearchEntryListComponent_ng_template_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r5 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "ion-header")(1, "ion-toolbar");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](2, "ion-title");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](3, "ion-buttons", 11)(4, "ion-button", 12);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function SearchEntryListComponent_ng_template_3_Template_ion_button_click_4_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r5);
      const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r3.isModalOpen = false);
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](5, "Close");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](6, "ion-content", 13);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](7, "mtd-entry", 14);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](7);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("entry", ctx_r3.modalEntry);
  }
}
class SearchEntryListComponent {
  constructor(dataService) {
    this.dataService = dataService;
    this.edit = false;
    this.maxResults = 20; // this can make it super slow if it's unconstrained
    this.isModalOpen = false;
    this.$entriesHash = this.dataService.$entriesHash;
  }
  ngOnInit() {}
  showModal(entry) {
    this.modalEntry = entry;
    this.isModalOpen = true;
  }
  setOpen(value) {
    this.isModalOpen = value;
  }
  didDismiss() {
    this.isModalOpen = false;
  }
  highlight(result, lang) {
    // highlighting in this interface only happens on either words or definitions
    const key = lang === 'L1' ? 'word' : 'definition';
    const terms = this.$entriesHash.value[result[1]][key].split(/\s+/);
    const htmlTerms = terms.map(word => `<span>${word}</span>`);
    result[2].forEach(match => {
      if (match[0] === key) {
        htmlTerms[match[1]] = `<span class="langMatched">${terms[match[1]]}</span>`;
      }
    });
    return htmlTerms.join(' ');
  }
  ngOnChanges() {
    if (this.parentEdit !== undefined) {
      this.edit = this.parentEdit;
    }
  }
  trackByFn(index, item) {
    return item.entryID;
  }
  static #_ = this.ɵfac = function SearchEntryListComponent_Factory(t) {
    return new (t || SearchEntryListComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService));
  };
  static #_2 = this.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdefineComponent"]({
    type: SearchEntryListComponent,
    selectors: [["mtd-search-entry-list"]],
    inputs: {
      parentEdit: "parentEdit",
      entries: "entries",
      searchterm: "searchterm",
      threshold: "threshold"
    },
    features: [_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵNgOnChangesFeature"]],
    decls: 4,
    vars: 2,
    consts: [[1, "browseElements"], [4, "ngIf"], [3, "didDismiss", "isOpen"], ["class", "matchContainer", "text-wrap", "", 3, "click", 4, "ngFor", "ngForOf"], ["text-wrap", "", 1, "matchContainer", 3, "click"], ["color", "danger", 3, "checked", 4, "ngIf"], [1, "matchLeftContainer"], [1, "response", "matchLeftDiv", 3, "innerHTML"], [1, "matchRightContainer"], [1, "response", "matchRightDiv", 3, "innerHTML"], ["color", "danger", 3, "checked"], ["slot", "end"], [3, "click"], [1, "ion-padding"], [3, "entry"]],
    template: function SearchEntryListComponent_Template(rf, ctx) {
      if (rf & 1) {
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "div", 0);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](1, SearchEntryListComponent_ion_list_1_Template, 3, 3, "ion-list", 1);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "ion-modal", 2);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("didDismiss", function SearchEntryListComponent_Template_ion_modal_didDismiss_2_listener() {
          return ctx.didDismiss();
        });
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](3, SearchEntryListComponent_ng_template_3_Template, 8, 1, "ng-template");
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      }
      if (rf & 2) {
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.entries.length > 0);
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("isOpen", ctx.isModalOpen);
      }
    },
    dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_3__.NgForOf, _angular_common__WEBPACK_IMPORTED_MODULE_3__.NgIf, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonButton, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonButtons, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonCheckbox, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonContent, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonHeader, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonItem, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonLabel, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonList, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonTitle, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonToolbar, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.IonModal, _ionic_angular__WEBPACK_IMPORTED_MODULE_4__.BooleanValueAccessor, _entry_component__WEBPACK_IMPORTED_MODULE_1__.EntryComponent, _angular_common__WEBPACK_IMPORTED_MODULE_3__.AsyncPipe],
    styles: ["/** Ionic CSS Variables **/\n:root {\n  /** primary **/\n  --ion-color-primary: #3880ff;\n  --ion-color-primary-rgb: 56, 128, 255;\n  --ion-color-primary-contrast: #ffffff;\n  --ion-color-primary-contrast-rgb: 255, 255, 255;\n  --ion-color-primary-shade: #3171e0;\n  --ion-color-primary-tint: #4c8dff;\n  /** secondary **/\n  --ion-color-secondary: #3dc2ff;\n  --ion-color-secondary-rgb: 61, 194, 255;\n  --ion-color-secondary-contrast: #ffffff;\n  --ion-color-secondary-contrast-rgb: 255, 255, 255;\n  --ion-color-secondary-shade: #36abe0;\n  --ion-color-secondary-tint: #50c8ff;\n  /** tertiary **/\n  --ion-color-tertiary: #5260ff;\n  --ion-color-tertiary-rgb: 82, 96, 255;\n  --ion-color-tertiary-contrast: #ffffff;\n  --ion-color-tertiary-contrast-rgb: 255, 255, 255;\n  --ion-color-tertiary-shade: #4854e0;\n  --ion-color-tertiary-tint: #6370ff;\n  /** success **/\n  --ion-color-success: #2dd36f;\n  --ion-color-success-rgb: 45, 211, 111;\n  --ion-color-success-contrast: #ffffff;\n  --ion-color-success-contrast-rgb: 255, 255, 255;\n  --ion-color-success-shade: #28ba62;\n  --ion-color-success-tint: #42d77d;\n  /** warning **/\n  --ion-color-warning: #ffc409;\n  --ion-color-warning-rgb: 255, 196, 9;\n  --ion-color-warning-contrast: #000000;\n  --ion-color-warning-contrast-rgb: 0, 0, 0;\n  --ion-color-warning-shade: #e0ac08;\n  --ion-color-warning-tint: #ffca22;\n  /** danger **/\n  --ion-color-danger: #eb445a;\n  --ion-color-danger-rgb: 235, 68, 90;\n  --ion-color-danger-contrast: #ffffff;\n  --ion-color-danger-contrast-rgb: 255, 255, 255;\n  --ion-color-danger-shade: #cf3c4f;\n  --ion-color-danger-tint: #ed576b;\n  /** dark **/\n  --ion-color-dark: #222428;\n  --ion-color-dark-rgb: 34, 36, 40;\n  --ion-color-dark-contrast: #ffffff;\n  --ion-color-dark-contrast-rgb: 255, 255, 255;\n  --ion-color-dark-shade: #1e2023;\n  --ion-color-dark-tint: #383a3e;\n  /** medium **/\n  --ion-color-medium: #92949c;\n  --ion-color-medium-rgb: 146, 148, 156;\n  --ion-color-medium-contrast: #ffffff;\n  --ion-color-medium-contrast-rgb: 255, 255, 255;\n  --ion-color-medium-shade: #808289;\n  --ion-color-medium-tint: #9d9fa6;\n  /** light **/\n  --ion-color-light: #f4f5f8;\n  --ion-color-light-rgb: 244, 245, 248;\n  --ion-color-light-contrast: #000000;\n  --ion-color-light-contrast-rgb: 0, 0, 0;\n  --ion-color-light-shade: #d7d8da;\n  --ion-color-light-tint: #f5f6f9;\n}\n\n@media (prefers-color-scheme: dark) {\n  /*\n   * Dark Colors\n   * -------------------------------------------\n   */\n  body {\n    --ion-color-primary: #428cff;\n    --ion-color-primary-rgb: 66, 140, 255;\n    --ion-color-primary-contrast: #ffffff;\n    --ion-color-primary-contrast-rgb: 255, 255, 255;\n    --ion-color-primary-shade: #3a7be0;\n    --ion-color-primary-tint: #5598ff;\n    --ion-color-secondary: #50c8ff;\n    --ion-color-secondary-rgb: 80, 200, 255;\n    --ion-color-secondary-contrast: #ffffff;\n    --ion-color-secondary-contrast-rgb: 255, 255, 255;\n    --ion-color-secondary-shade: #46b0e0;\n    --ion-color-secondary-tint: #62ceff;\n    --ion-color-tertiary: #6a64ff;\n    --ion-color-tertiary-rgb: 106, 100, 255;\n    --ion-color-tertiary-contrast: #ffffff;\n    --ion-color-tertiary-contrast-rgb: 255, 255, 255;\n    --ion-color-tertiary-shade: #5d58e0;\n    --ion-color-tertiary-tint: #7974ff;\n    --ion-color-success: #2fdf75;\n    --ion-color-success-rgb: 47, 223, 117;\n    --ion-color-success-contrast: #000000;\n    --ion-color-success-contrast-rgb: 0, 0, 0;\n    --ion-color-success-shade: #29c467;\n    --ion-color-success-tint: #44e283;\n    --ion-color-warning: #ffd534;\n    --ion-color-warning-rgb: 255, 213, 52;\n    --ion-color-warning-contrast: #000000;\n    --ion-color-warning-contrast-rgb: 0, 0, 0;\n    --ion-color-warning-shade: #e0bb2e;\n    --ion-color-warning-tint: #ffd948;\n    --ion-color-danger: #ff4961;\n    --ion-color-danger-rgb: 255, 73, 97;\n    --ion-color-danger-contrast: #ffffff;\n    --ion-color-danger-contrast-rgb: 255, 255, 255;\n    --ion-color-danger-shade: #e04055;\n    --ion-color-danger-tint: #ff5b71;\n    --ion-color-dark: #f4f5f8;\n    --ion-color-dark-rgb: 244, 245, 248;\n    --ion-color-dark-contrast: #000000;\n    --ion-color-dark-contrast-rgb: 0, 0, 0;\n    --ion-color-dark-shade: #d7d8da;\n    --ion-color-dark-tint: #f5f6f9;\n    --ion-color-medium: #989aa2;\n    --ion-color-medium-rgb: 152, 154, 162;\n    --ion-color-medium-contrast: #000000;\n    --ion-color-medium-contrast-rgb: 0, 0, 0;\n    --ion-color-medium-shade: #86888f;\n    --ion-color-medium-tint: #a2a4ab;\n    --ion-color-light: #222428;\n    --ion-color-light-rgb: 34, 36, 40;\n    --ion-color-light-contrast: #ffffff;\n    --ion-color-light-contrast-rgb: 255, 255, 255;\n    --ion-color-light-shade: #1e2023;\n    --ion-color-light-tint: #383a3e;\n  }\n  /*\n   * iOS Dark Theme\n   * -------------------------------------------\n   */\n  .ios body {\n    --ion-background-color: #000000;\n    --ion-background-color-rgb: 0, 0, 0;\n    --ion-text-color: #ffffff;\n    --ion-text-color-rgb: 255, 255, 255;\n    --ion-color-step-50: #0d0d0d;\n    --ion-color-step-100: #1a1a1a;\n    --ion-color-step-150: #262626;\n    --ion-color-step-200: #333333;\n    --ion-color-step-250: #404040;\n    --ion-color-step-300: #4d4d4d;\n    --ion-color-step-350: #595959;\n    --ion-color-step-400: #666666;\n    --ion-color-step-450: #737373;\n    --ion-color-step-500: #808080;\n    --ion-color-step-550: #8c8c8c;\n    --ion-color-step-600: #999999;\n    --ion-color-step-650: #a6a6a6;\n    --ion-color-step-700: #b3b3b3;\n    --ion-color-step-750: #bfbfbf;\n    --ion-color-step-800: #cccccc;\n    --ion-color-step-850: #d9d9d9;\n    --ion-color-step-900: #e6e6e6;\n    --ion-color-step-950: #f2f2f2;\n    --ion-item-background: #000000;\n    --ion-card-background: #1c1c1d;\n  }\n  .ios ion-modal {\n    --ion-background-color: var(--ion-color-step-100);\n    --ion-toolbar-background: var(--ion-color-step-150);\n    --ion-toolbar-border-color: var(--ion-color-step-250);\n  }\n  /*\n   * Material Design Dark Theme\n   * -------------------------------------------\n   */\n  .md body {\n    --ion-background-color: #121212;\n    --ion-background-color-rgb: 18, 18, 18;\n    --ion-text-color: #ffffff;\n    --ion-text-color-rgb: 255, 255, 255;\n    --ion-border-color: #222222;\n    --ion-color-step-50: #1e1e1e;\n    --ion-color-step-100: #2a2a2a;\n    --ion-color-step-150: #363636;\n    --ion-color-step-200: #414141;\n    --ion-color-step-250: #4d4d4d;\n    --ion-color-step-300: #595959;\n    --ion-color-step-350: #656565;\n    --ion-color-step-400: #717171;\n    --ion-color-step-450: #7d7d7d;\n    --ion-color-step-500: #898989;\n    --ion-color-step-550: #949494;\n    --ion-color-step-600: #a0a0a0;\n    --ion-color-step-650: #acacac;\n    --ion-color-step-700: #b8b8b8;\n    --ion-color-step-750: #c4c4c4;\n    --ion-color-step-800: #d0d0d0;\n    --ion-color-step-850: #dbdbdb;\n    --ion-color-step-900: #e7e7e7;\n    --ion-color-step-950: #f3f3f3;\n    --ion-item-background: #1e1e1e;\n    --ion-toolbar-background: #1f1f1f;\n    --ion-tab-bar-background: #1f1f1f;\n    --ion-card-background: #1e1e1e;\n  }\n}\n.browseElements {\n  margin: auto;\n  height: auto;\n  width: auto;\n  text-align: center;\n  background-color: var(--ion-color-medium);\n}\n\n.browseElements {\n  margin: auto;\n  height: auto;\n  width: auto;\n  text-align: center !important;\n  background-color: var(--ion-color-medium);\n}\n\n.matchContainer {\n  margin: 1em 0;\n  text-align: center;\n}\n\n.matchLeftDiv {\n  margin-right: 0.2em;\n  text-align: left;\n}\n\n.matchLeftContainer,\n.matchRightContainer {\n  display: initial;\n}\n\n.matchRightDiv {\n  margin-left: 0.2em;\n}\n\n.matchResponse {\n  margin: 2.5em 0 0.75em 0;\n  text-decoration: underline;\n}\n\n.browseL1 {\n  color: var(--ion-color-secondary);\n}\n\n.matchLeftDiv .langMatched {\n  color: var(--ion-color-secondary);\n  font-weight: 900;\n}\n\n.matchRightDiv .langMatched {\n  color: var(--ion-color-secondary);\n  font-weight: 900;\n}\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3BhY2thZ2VzL210ZC1tb2JpbGUtdWkvc3JjL3RoZW1lL3ZhcmlhYmxlcy5zY3NzIiwid2VicGFjazovLy4vcGFja2FnZXMvbXRkLW1vYmlsZS11aS9zcmMvYXBwL3NoYXJlZC9lbnRyeS1saXN0LmNvbXBvbmVudC5zY3NzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUdBLDBCQUFBO0FBQ0E7RUFDRSxjQUFBO0VBQ0EsNEJBQUE7RUFDQSxxQ0FBQTtFQUNBLHFDQUFBO0VBQ0EsK0NBQUE7RUFDQSxrQ0FBQTtFQUNBLGlDQUFBO0VBRUEsZ0JBQUE7RUFDQSw4QkFBQTtFQUNBLHVDQUFBO0VBQ0EsdUNBQUE7RUFDQSxpREFBQTtFQUNBLG9DQUFBO0VBQ0EsbUNBQUE7RUFFQSxlQUFBO0VBQ0EsNkJBQUE7RUFDQSxxQ0FBQTtFQUNBLHNDQUFBO0VBQ0EsZ0RBQUE7RUFDQSxtQ0FBQTtFQUNBLGtDQUFBO0VBRUEsY0FBQTtFQUNBLDRCQUFBO0VBQ0EscUNBQUE7RUFDQSxxQ0FBQTtFQUNBLCtDQUFBO0VBQ0Esa0NBQUE7RUFDQSxpQ0FBQTtFQUVBLGNBQUE7RUFDQSw0QkFBQTtFQUNBLG9DQUFBO0VBQ0EscUNBQUE7RUFDQSx5Q0FBQTtFQUNBLGtDQUFBO0VBQ0EsaUNBQUE7RUFFQSxhQUFBO0VBQ0EsMkJBQUE7RUFDQSxtQ0FBQTtFQUNBLG9DQUFBO0VBQ0EsOENBQUE7RUFDQSxpQ0FBQTtFQUNBLGdDQUFBO0VBRUEsV0FBQTtFQUNBLHlCQUFBO0VBQ0EsZ0NBQUE7RUFDQSxrQ0FBQTtFQUNBLDRDQUFBO0VBQ0EsK0JBQUE7RUFDQSw4QkFBQTtFQUVBLGFBQUE7RUFDQSwyQkFBQTtFQUNBLHFDQUFBO0VBQ0Esb0NBQUE7RUFDQSw4Q0FBQTtFQUNBLGlDQUFBO0VBQ0EsZ0NBQUE7RUFFQSxZQUFBO0VBQ0EsMEJBQUE7RUFDQSxvQ0FBQTtFQUNBLG1DQUFBO0VBQ0EsdUNBQUE7RUFDQSxnQ0FBQTtFQUNBLCtCQUFBO0FDVkY7O0FEYUE7RUFDRTs7O0lBQUE7RUFLQTtJQUNFLDRCQUFBO0lBQ0EscUNBQUE7SUFDQSxxQ0FBQTtJQUNBLCtDQUFBO0lBQ0Esa0NBQUE7SUFDQSxpQ0FBQTtJQUVBLDhCQUFBO0lBQ0EsdUNBQUE7SUFDQSx1Q0FBQTtJQUNBLGlEQUFBO0lBQ0Esb0NBQUE7SUFDQSxtQ0FBQTtJQUVBLDZCQUFBO0lBQ0EsdUNBQUE7SUFDQSxzQ0FBQTtJQUNBLGdEQUFBO0lBQ0EsbUNBQUE7SUFDQSxrQ0FBQTtJQUVBLDRCQUFBO0lBQ0EscUNBQUE7SUFDQSxxQ0FBQTtJQUNBLHlDQUFBO0lBQ0Esa0NBQUE7SUFDQSxpQ0FBQTtJQUVBLDRCQUFBO0lBQ0EscUNBQUE7SUFDQSxxQ0FBQTtJQUNBLHlDQUFBO0lBQ0Esa0NBQUE7SUFDQSxpQ0FBQTtJQUVBLDJCQUFBO0lBQ0EsbUNBQUE7SUFDQSxvQ0FBQTtJQUNBLDhDQUFBO0lBQ0EsaUNBQUE7SUFDQSxnQ0FBQTtJQUVBLHlCQUFBO0lBQ0EsbUNBQUE7SUFDQSxrQ0FBQTtJQUNBLHNDQUFBO0lBQ0EsK0JBQUE7SUFDQSw4QkFBQTtJQUVBLDJCQUFBO0lBQ0EscUNBQUE7SUFDQSxvQ0FBQTtJQUNBLHdDQUFBO0lBQ0EsaUNBQUE7SUFDQSxnQ0FBQTtJQUVBLDBCQUFBO0lBQ0EsaUNBQUE7SUFDQSxtQ0FBQTtJQUNBLDZDQUFBO0lBQ0EsZ0NBQUE7SUFDQSwrQkFBQTtFQ25CRjtFRHNCQTs7O0lBQUE7RUFLQTtJQUNFLCtCQUFBO0lBQ0EsbUNBQUE7SUFFQSx5QkFBQTtJQUNBLG1DQUFBO0lBRUEsNEJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFFQSw4QkFBQTtJQUVBLDhCQUFBO0VDekJGO0VENEJBO0lBQ0UsaURBQUE7SUFDQSxtREFBQTtJQUNBLHFEQUFBO0VDMUJGO0VENkJBOzs7SUFBQTtFQUtBO0lBQ0UsK0JBQUE7SUFDQSxzQ0FBQTtJQUVBLHlCQUFBO0lBQ0EsbUNBQUE7SUFFQSwyQkFBQTtJQUVBLDRCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBQ0EsNkJBQUE7SUFDQSw2QkFBQTtJQUNBLDZCQUFBO0lBRUEsOEJBQUE7SUFFQSxpQ0FBQTtJQUVBLGlDQUFBO0lBRUEsOEJBQUE7RUNuQ0Y7QUFDRjtBQXBNQTtFQUNFLFlBQUE7RUFDQSxZQUFBO0VBQ0EsV0FBQTtFQUNBLGtCQUFBO0VBQ0EseUNBQUE7QUFzTUY7O0FBbk1BO0VBQ0UsWUFBQTtFQUNBLFlBQUE7RUFDQSxXQUFBO0VBQ0EsNkJBQUE7RUFDQSx5Q0FBQTtBQXNNRjs7QUFuTUE7RUFDRSxhQUFBO0VBQ0Esa0JBQUE7QUFzTUY7O0FBbk1BO0VBQ0UsbUJBQUE7RUFDQSxnQkFBQTtBQXNNRjs7QUFuTUE7O0VBRUUsZ0JBQUE7QUFzTUY7O0FBbk1BO0VBQ0Usa0JBQUE7QUFzTUY7O0FBbk1BO0VBQ0Usd0JBQUE7RUFDQSwwQkFBQTtBQXNNRjs7QUFuTUE7RUFDRSxpQ0FBQTtBQXNNRjs7QUFuTUE7RUFDRSxpQ0FBQTtFQUVBLGdCQUFBO0FBcU1GOztBQWpNQTtFQUNFLGlDQUFBO0VBQ0EsZ0JBQUE7QUFvTUYiLCJzb3VyY2VzQ29udGVudCI6WyIvLyBJb25pYyBWYXJpYWJsZXMgYW5kIFRoZW1pbmcuIEZvciBtb3JlIGluZm8sIHBsZWFzZSBzZWU6XG4vLyBodHRwOi8vaW9uaWNmcmFtZXdvcmsuY29tL2RvY3MvdGhlbWluZy9cblxuLyoqIElvbmljIENTUyBWYXJpYWJsZXMgKiovXG46cm9vdCB7XG4gIC8qKiBwcmltYXJ5ICoqL1xuICAtLWlvbi1jb2xvci1wcmltYXJ5OiAjMzg4MGZmO1xuICAtLWlvbi1jb2xvci1wcmltYXJ5LXJnYjogNTYsIDEyOCwgMjU1O1xuICAtLWlvbi1jb2xvci1wcmltYXJ5LWNvbnRyYXN0OiAjZmZmZmZmO1xuICAtLWlvbi1jb2xvci1wcmltYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgLS1pb24tY29sb3ItcHJpbWFyeS1zaGFkZTogIzMxNzFlMDtcbiAgLS1pb24tY29sb3ItcHJpbWFyeS10aW50OiAjNGM4ZGZmO1xuXG4gIC8qKiBzZWNvbmRhcnkgKiovXG4gIC0taW9uLWNvbG9yLXNlY29uZGFyeTogIzNkYzJmZjtcbiAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LXJnYjogNjEsIDE5NCwgMjU1O1xuICAtLWlvbi1jb2xvci1zZWNvbmRhcnktY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLXNlY29uZGFyeS1jb250cmFzdC1yZ2I6IDI1NSwgMjU1LCAyNTU7XG4gIC0taW9uLWNvbG9yLXNlY29uZGFyeS1zaGFkZTogIzM2YWJlMDtcbiAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LXRpbnQ6ICM1MGM4ZmY7XG5cbiAgLyoqIHRlcnRpYXJ5ICoqL1xuICAtLWlvbi1jb2xvci10ZXJ0aWFyeTogIzUyNjBmZjtcbiAgLS1pb24tY29sb3ItdGVydGlhcnktcmdiOiA4MiwgOTYsIDI1NTtcbiAgLS1pb24tY29sb3ItdGVydGlhcnktY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLXRlcnRpYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgLS1pb24tY29sb3ItdGVydGlhcnktc2hhZGU6ICM0ODU0ZTA7XG4gIC0taW9uLWNvbG9yLXRlcnRpYXJ5LXRpbnQ6ICM2MzcwZmY7XG5cbiAgLyoqIHN1Y2Nlc3MgKiovXG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3M6ICMyZGQzNmY7XG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3MtcmdiOiA0NSwgMjExLCAxMTE7XG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3MtY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLXN1Y2Nlc3MtY29udHJhc3QtcmdiOiAyNTUsIDI1NSwgMjU1O1xuICAtLWlvbi1jb2xvci1zdWNjZXNzLXNoYWRlOiAjMjhiYTYyO1xuICAtLWlvbi1jb2xvci1zdWNjZXNzLXRpbnQ6ICM0MmQ3N2Q7XG5cbiAgLyoqIHdhcm5pbmcgKiovXG4gIC0taW9uLWNvbG9yLXdhcm5pbmc6ICNmZmM0MDk7XG4gIC0taW9uLWNvbG9yLXdhcm5pbmctcmdiOiAyNTUsIDE5NiwgOTtcbiAgLS1pb24tY29sb3Itd2FybmluZy1jb250cmFzdDogIzAwMDAwMDtcbiAgLS1pb24tY29sb3Itd2FybmluZy1jb250cmFzdC1yZ2I6IDAsIDAsIDA7XG4gIC0taW9uLWNvbG9yLXdhcm5pbmctc2hhZGU6ICNlMGFjMDg7XG4gIC0taW9uLWNvbG9yLXdhcm5pbmctdGludDogI2ZmY2EyMjtcblxuICAvKiogZGFuZ2VyICoqL1xuICAtLWlvbi1jb2xvci1kYW5nZXI6ICNlYjQ0NWE7XG4gIC0taW9uLWNvbG9yLWRhbmdlci1yZ2I6IDIzNSwgNjgsIDkwO1xuICAtLWlvbi1jb2xvci1kYW5nZXItY29udHJhc3Q6ICNmZmZmZmY7XG4gIC0taW9uLWNvbG9yLWRhbmdlci1jb250cmFzdC1yZ2I6IDI1NSwgMjU1LCAyNTU7XG4gIC0taW9uLWNvbG9yLWRhbmdlci1zaGFkZTogI2NmM2M0ZjtcbiAgLS1pb24tY29sb3ItZGFuZ2VyLXRpbnQ6ICNlZDU3NmI7XG5cbiAgLyoqIGRhcmsgKiovXG4gIC0taW9uLWNvbG9yLWRhcms6ICMyMjI0Mjg7XG4gIC0taW9uLWNvbG9yLWRhcmstcmdiOiAzNCwgMzYsIDQwO1xuICAtLWlvbi1jb2xvci1kYXJrLWNvbnRyYXN0OiAjZmZmZmZmO1xuICAtLWlvbi1jb2xvci1kYXJrLWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgLS1pb24tY29sb3ItZGFyay1zaGFkZTogIzFlMjAyMztcbiAgLS1pb24tY29sb3ItZGFyay10aW50OiAjMzgzYTNlO1xuXG4gIC8qKiBtZWRpdW0gKiovXG4gIC0taW9uLWNvbG9yLW1lZGl1bTogIzkyOTQ5YztcbiAgLS1pb24tY29sb3ItbWVkaXVtLXJnYjogMTQ2LCAxNDgsIDE1NjtcbiAgLS1pb24tY29sb3ItbWVkaXVtLWNvbnRyYXN0OiAjZmZmZmZmO1xuICAtLWlvbi1jb2xvci1tZWRpdW0tY29udHJhc3QtcmdiOiAyNTUsIDI1NSwgMjU1O1xuICAtLWlvbi1jb2xvci1tZWRpdW0tc2hhZGU6ICM4MDgyODk7XG4gIC0taW9uLWNvbG9yLW1lZGl1bS10aW50OiAjOWQ5ZmE2O1xuXG4gIC8qKiBsaWdodCAqKi9cbiAgLS1pb24tY29sb3ItbGlnaHQ6ICNmNGY1Zjg7XG4gIC0taW9uLWNvbG9yLWxpZ2h0LXJnYjogMjQ0LCAyNDUsIDI0ODtcbiAgLS1pb24tY29sb3ItbGlnaHQtY29udHJhc3Q6ICMwMDAwMDA7XG4gIC0taW9uLWNvbG9yLWxpZ2h0LWNvbnRyYXN0LXJnYjogMCwgMCwgMDtcbiAgLS1pb24tY29sb3ItbGlnaHQtc2hhZGU6ICNkN2Q4ZGE7XG4gIC0taW9uLWNvbG9yLWxpZ2h0LXRpbnQ6ICNmNWY2Zjk7XG59XG5cbkBtZWRpYSAocHJlZmVycy1jb2xvci1zY2hlbWU6IGRhcmspIHtcbiAgLypcbiAgICogRGFyayBDb2xvcnNcbiAgICogLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxuICAgKi9cblxuICBib2R5IHtcbiAgICAtLWlvbi1jb2xvci1wcmltYXJ5OiAjNDI4Y2ZmO1xuICAgIC0taW9uLWNvbG9yLXByaW1hcnktcmdiOiA2NiwgMTQwLCAyNTU7XG4gICAgLS1pb24tY29sb3ItcHJpbWFyeS1jb250cmFzdDogI2ZmZmZmZjtcbiAgICAtLWlvbi1jb2xvci1wcmltYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgICAtLWlvbi1jb2xvci1wcmltYXJ5LXNoYWRlOiAjM2E3YmUwO1xuICAgIC0taW9uLWNvbG9yLXByaW1hcnktdGludDogIzU1OThmZjtcblxuICAgIC0taW9uLWNvbG9yLXNlY29uZGFyeTogIzUwYzhmZjtcbiAgICAtLWlvbi1jb2xvci1zZWNvbmRhcnktcmdiOiA4MCwgMjAwLCAyNTU7XG4gICAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LWNvbnRyYXN0OiAjZmZmZmZmO1xuICAgIC0taW9uLWNvbG9yLXNlY29uZGFyeS1jb250cmFzdC1yZ2I6IDI1NSwgMjU1LCAyNTU7XG4gICAgLS1pb24tY29sb3Itc2Vjb25kYXJ5LXNoYWRlOiAjNDZiMGUwO1xuICAgIC0taW9uLWNvbG9yLXNlY29uZGFyeS10aW50OiAjNjJjZWZmO1xuXG4gICAgLS1pb24tY29sb3ItdGVydGlhcnk6ICM2YTY0ZmY7XG4gICAgLS1pb24tY29sb3ItdGVydGlhcnktcmdiOiAxMDYsIDEwMCwgMjU1O1xuICAgIC0taW9uLWNvbG9yLXRlcnRpYXJ5LWNvbnRyYXN0OiAjZmZmZmZmO1xuICAgIC0taW9uLWNvbG9yLXRlcnRpYXJ5LWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgICAtLWlvbi1jb2xvci10ZXJ0aWFyeS1zaGFkZTogIzVkNThlMDtcbiAgICAtLWlvbi1jb2xvci10ZXJ0aWFyeS10aW50OiAjNzk3NGZmO1xuXG4gICAgLS1pb24tY29sb3Itc3VjY2VzczogIzJmZGY3NTtcbiAgICAtLWlvbi1jb2xvci1zdWNjZXNzLXJnYjogNDcsIDIyMywgMTE3O1xuICAgIC0taW9uLWNvbG9yLXN1Y2Nlc3MtY29udHJhc3Q6ICMwMDAwMDA7XG4gICAgLS1pb24tY29sb3Itc3VjY2Vzcy1jb250cmFzdC1yZ2I6IDAsIDAsIDA7XG4gICAgLS1pb24tY29sb3Itc3VjY2Vzcy1zaGFkZTogIzI5YzQ2NztcbiAgICAtLWlvbi1jb2xvci1zdWNjZXNzLXRpbnQ6ICM0NGUyODM7XG5cbiAgICAtLWlvbi1jb2xvci13YXJuaW5nOiAjZmZkNTM0O1xuICAgIC0taW9uLWNvbG9yLXdhcm5pbmctcmdiOiAyNTUsIDIxMywgNTI7XG4gICAgLS1pb24tY29sb3Itd2FybmluZy1jb250cmFzdDogIzAwMDAwMDtcbiAgICAtLWlvbi1jb2xvci13YXJuaW5nLWNvbnRyYXN0LXJnYjogMCwgMCwgMDtcbiAgICAtLWlvbi1jb2xvci13YXJuaW5nLXNoYWRlOiAjZTBiYjJlO1xuICAgIC0taW9uLWNvbG9yLXdhcm5pbmctdGludDogI2ZmZDk0ODtcblxuICAgIC0taW9uLWNvbG9yLWRhbmdlcjogI2ZmNDk2MTtcbiAgICAtLWlvbi1jb2xvci1kYW5nZXItcmdiOiAyNTUsIDczLCA5NztcbiAgICAtLWlvbi1jb2xvci1kYW5nZXItY29udHJhc3Q6ICNmZmZmZmY7XG4gICAgLS1pb24tY29sb3ItZGFuZ2VyLWNvbnRyYXN0LXJnYjogMjU1LCAyNTUsIDI1NTtcbiAgICAtLWlvbi1jb2xvci1kYW5nZXItc2hhZGU6ICNlMDQwNTU7XG4gICAgLS1pb24tY29sb3ItZGFuZ2VyLXRpbnQ6ICNmZjViNzE7XG5cbiAgICAtLWlvbi1jb2xvci1kYXJrOiAjZjRmNWY4O1xuICAgIC0taW9uLWNvbG9yLWRhcmstcmdiOiAyNDQsIDI0NSwgMjQ4O1xuICAgIC0taW9uLWNvbG9yLWRhcmstY29udHJhc3Q6ICMwMDAwMDA7XG4gICAgLS1pb24tY29sb3ItZGFyay1jb250cmFzdC1yZ2I6IDAsIDAsIDA7XG4gICAgLS1pb24tY29sb3ItZGFyay1zaGFkZTogI2Q3ZDhkYTtcbiAgICAtLWlvbi1jb2xvci1kYXJrLXRpbnQ6ICNmNWY2Zjk7XG5cbiAgICAtLWlvbi1jb2xvci1tZWRpdW06ICM5ODlhYTI7XG4gICAgLS1pb24tY29sb3ItbWVkaXVtLXJnYjogMTUyLCAxNTQsIDE2MjtcbiAgICAtLWlvbi1jb2xvci1tZWRpdW0tY29udHJhc3Q6ICMwMDAwMDA7XG4gICAgLS1pb24tY29sb3ItbWVkaXVtLWNvbnRyYXN0LXJnYjogMCwgMCwgMDtcbiAgICAtLWlvbi1jb2xvci1tZWRpdW0tc2hhZGU6ICM4Njg4OGY7XG4gICAgLS1pb24tY29sb3ItbWVkaXVtLXRpbnQ6ICNhMmE0YWI7XG5cbiAgICAtLWlvbi1jb2xvci1saWdodDogIzIyMjQyODtcbiAgICAtLWlvbi1jb2xvci1saWdodC1yZ2I6IDM0LCAzNiwgNDA7XG4gICAgLS1pb24tY29sb3ItbGlnaHQtY29udHJhc3Q6ICNmZmZmZmY7XG4gICAgLS1pb24tY29sb3ItbGlnaHQtY29udHJhc3QtcmdiOiAyNTUsIDI1NSwgMjU1O1xuICAgIC0taW9uLWNvbG9yLWxpZ2h0LXNoYWRlOiAjMWUyMDIzO1xuICAgIC0taW9uLWNvbG9yLWxpZ2h0LXRpbnQ6ICMzODNhM2U7XG4gIH1cblxuICAvKlxuICAgKiBpT1MgRGFyayBUaGVtZVxuICAgKiAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG4gICAqL1xuXG4gIC5pb3MgYm9keSB7XG4gICAgLS1pb24tYmFja2dyb3VuZC1jb2xvcjogIzAwMDAwMDtcbiAgICAtLWlvbi1iYWNrZ3JvdW5kLWNvbG9yLXJnYjogMCwgMCwgMDtcblxuICAgIC0taW9uLXRleHQtY29sb3I6ICNmZmZmZmY7XG4gICAgLS1pb24tdGV4dC1jb2xvci1yZ2I6IDI1NSwgMjU1LCAyNTU7XG5cbiAgICAtLWlvbi1jb2xvci1zdGVwLTUwOiAjMGQwZDBkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTAwOiAjMWExYTFhO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTUwOiAjMjYyNjI2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjAwOiAjMzMzMzMzO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjUwOiAjNDA0MDQwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzAwOiAjNGQ0ZDRkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzUwOiAjNTk1OTU5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDAwOiAjNjY2NjY2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDUwOiAjNzM3MzczO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTAwOiAjODA4MDgwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTUwOiAjOGM4YzhjO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjAwOiAjOTk5OTk5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjUwOiAjYTZhNmE2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzAwOiAjYjNiM2IzO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzUwOiAjYmZiZmJmO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODAwOiAjY2NjY2NjO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODUwOiAjZDlkOWQ5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTAwOiAjZTZlNmU2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTUwOiAjZjJmMmYyO1xuXG4gICAgLS1pb24taXRlbS1iYWNrZ3JvdW5kOiAjMDAwMDAwO1xuXG4gICAgLS1pb24tY2FyZC1iYWNrZ3JvdW5kOiAjMWMxYzFkO1xuICB9XG5cbiAgLmlvcyBpb24tbW9kYWwge1xuICAgIC0taW9uLWJhY2tncm91bmQtY29sb3I6IHZhcigtLWlvbi1jb2xvci1zdGVwLTEwMCk7XG4gICAgLS1pb24tdG9vbGJhci1iYWNrZ3JvdW5kOiB2YXIoLS1pb24tY29sb3Itc3RlcC0xNTApO1xuICAgIC0taW9uLXRvb2xiYXItYm9yZGVyLWNvbG9yOiB2YXIoLS1pb24tY29sb3Itc3RlcC0yNTApO1xuICB9XG5cbiAgLypcbiAgICogTWF0ZXJpYWwgRGVzaWduIERhcmsgVGhlbWVcbiAgICogLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxuICAgKi9cblxuICAubWQgYm9keSB7XG4gICAgLS1pb24tYmFja2dyb3VuZC1jb2xvcjogIzEyMTIxMjtcbiAgICAtLWlvbi1iYWNrZ3JvdW5kLWNvbG9yLXJnYjogMTgsIDE4LCAxODtcblxuICAgIC0taW9uLXRleHQtY29sb3I6ICNmZmZmZmY7XG4gICAgLS1pb24tdGV4dC1jb2xvci1yZ2I6IDI1NSwgMjU1LCAyNTU7XG5cbiAgICAtLWlvbi1ib3JkZXItY29sb3I6ICMyMjIyMjI7XG5cbiAgICAtLWlvbi1jb2xvci1zdGVwLTUwOiAjMWUxZTFlO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTAwOiAjMmEyYTJhO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMTUwOiAjMzYzNjM2O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjAwOiAjNDE0MTQxO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMjUwOiAjNGQ0ZDRkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzAwOiAjNTk1OTU5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtMzUwOiAjNjU2NTY1O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDAwOiAjNzE3MTcxO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNDUwOiAjN2Q3ZDdkO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTAwOiAjODk4OTg5O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNTUwOiAjOTQ5NDk0O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjAwOiAjYTBhMGEwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNjUwOiAjYWNhY2FjO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzAwOiAjYjhiOGI4O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtNzUwOiAjYzRjNGM0O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODAwOiAjZDBkMGQwO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtODUwOiAjZGJkYmRiO1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTAwOiAjZTdlN2U3O1xuICAgIC0taW9uLWNvbG9yLXN0ZXAtOTUwOiAjZjNmM2YzO1xuXG4gICAgLS1pb24taXRlbS1iYWNrZ3JvdW5kOiAjMWUxZTFlO1xuXG4gICAgLS1pb24tdG9vbGJhci1iYWNrZ3JvdW5kOiAjMWYxZjFmO1xuXG4gICAgLS1pb24tdGFiLWJhci1iYWNrZ3JvdW5kOiAjMWYxZjFmO1xuXG4gICAgLS1pb24tY2FyZC1iYWNrZ3JvdW5kOiAjMWUxZTFlO1xuICB9XG59XG4iLCJAaW1wb3J0ICcuLi8uLi90aGVtZS92YXJpYWJsZXMuc2Nzcyc7XG4vLyBlbnRyeS1saXN0IHtcbi5icm93c2VFbGVtZW50cyB7XG4gIG1hcmdpbjogYXV0bztcbiAgaGVpZ2h0OiBhdXRvO1xuICB3aWR0aDogYXV0bztcbiAgdGV4dC1hbGlnbjogY2VudGVyO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1pb24tY29sb3ItbWVkaXVtKTtcbn1cblxuLmJyb3dzZUVsZW1lbnRzIHtcbiAgbWFyZ2luOiBhdXRvO1xuICBoZWlnaHQ6IGF1dG87XG4gIHdpZHRoOiBhdXRvO1xuICB0ZXh0LWFsaWduOiBjZW50ZXIgIWltcG9ydGFudDtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0taW9uLWNvbG9yLW1lZGl1bSk7XG59XG5cbi5tYXRjaENvbnRhaW5lciB7XG4gIG1hcmdpbjogMWVtIDA7XG4gIHRleHQtYWxpZ246IGNlbnRlcjtcbn1cblxuLm1hdGNoTGVmdERpdiB7XG4gIG1hcmdpbi1yaWdodDogMC4yZW07XG4gIHRleHQtYWxpZ246IGxlZnQ7XG59XG5cbi5tYXRjaExlZnRDb250YWluZXIsXG4ubWF0Y2hSaWdodENvbnRhaW5lciB7XG4gIGRpc3BsYXk6IGluaXRpYWw7XG59XG5cbi5tYXRjaFJpZ2h0RGl2IHtcbiAgbWFyZ2luLWxlZnQ6IDAuMmVtO1xufVxuXG4ubWF0Y2hSZXNwb25zZSB7XG4gIG1hcmdpbjogMi41ZW0gMCAwLjc1ZW0gMDtcbiAgdGV4dC1kZWNvcmF0aW9uOiB1bmRlcmxpbmU7XG59XG5cbi5icm93c2VMMSB7XG4gIGNvbG9yOiB2YXIoLS1pb24tY29sb3Itc2Vjb25kYXJ5KTtcbn1cblxuLm1hdGNoTGVmdERpdiAubGFuZ01hdGNoZWQge1xuICBjb2xvcjogdmFyKC0taW9uLWNvbG9yLXNlY29uZGFyeSk7XG4gIC8vIGJvcmRlci1yYWRpdXM6IDE1cHg7XG4gIGZvbnQtd2VpZ2h0OiA5MDA7XG4gIC8vIHBhZGRpbmc6IDVweDtcbn1cblxuLm1hdGNoUmlnaHREaXYgLmxhbmdNYXRjaGVkIHtcbiAgY29sb3I6IHZhcigtLWlvbi1jb2xvci1zZWNvbmRhcnkpO1xuICBmb250LXdlaWdodDogOTAwO1xufVxuXG4vLyBpb24taXRlbSB7XG4vLyAgICAgdGV4dC1hbGlnbjogY2VudGVyO1xuLy8gfVxuLy8gfVxuIl0sInNvdXJjZVJvb3QiOiIifQ== */"],
    encapsulation: 2
  });
}

/***/ }),

/***/ 9540:
/*!*******************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/shared/settings.service.ts ***!
  \*******************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SettingsService: () => (/* binding */ SettingsService)
/* harmony export */ });
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! rxjs */ 5797);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ 7580);


class SettingsService {
  constructor() {
    this.showOptionalInfo$ = new rxjs__WEBPACK_IMPORTED_MODULE_0__.BehaviorSubject(sessionStorage.getItem('showOptionalInfo') == 'true');
    this.showOptionalInfo$.subscribe({
      'next': x => sessionStorage.setItem('showOptionalInfo', (x === true).toString())
    });
  }
  static #_ = this.ɵfac = function SettingsService_Factory(t) {
    return new (t || SettingsService)();
  };
  static #_2 = this.ɵprov = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineInjectable"]({
    token: SettingsService,
    factory: SettingsService.ɵfac,
    providedIn: 'root'
  });
}

/***/ }),

/***/ 3023:
/*!****************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/shared/shared.module.ts ***!
  \****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SharedModule: () => (/* binding */ SharedModule)
/* harmony export */ });
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _entry_list_component__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./entry-list.component */ 7530);
/* harmony import */ var _entry_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./entry.component */ 4247);
/* harmony import */ var _search_entry_list_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./search-entry-list.component */ 2155);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ 7580);






class SharedModule {
  static #_ = this.ɵfac = function SharedModule_Factory(t) {
    return new (t || SharedModule)();
  };
  static #_2 = this.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdefineNgModule"]({
    type: SharedModule
  });
  static #_3 = this.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdefineInjector"]({
    imports: [_angular_common__WEBPACK_IMPORTED_MODULE_4__.CommonModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonicModule]
  });
}
(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵsetNgModuleScope"](SharedModule, {
    declarations: [_entry_component__WEBPACK_IMPORTED_MODULE_1__.EntryComponent, _entry_list_component__WEBPACK_IMPORTED_MODULE_0__.EntryListComponent, _search_entry_list_component__WEBPACK_IMPORTED_MODULE_2__.SearchEntryListComponent],
    imports: [_angular_common__WEBPACK_IMPORTED_MODULE_4__.CommonModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonicModule],
    exports: [_entry_component__WEBPACK_IMPORTED_MODULE_1__.EntryComponent, _entry_list_component__WEBPACK_IMPORTED_MODULE_0__.EntryListComponent, _search_entry_list_component__WEBPACK_IMPORTED_MODULE_2__.SearchEntryListComponent]
  });
})();

/***/ }),

/***/ 3840:
/*!****************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/environments/environment.ts ***!
  \****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   environment: () => (/* binding */ environment)
/* harmony export */ });
const environment = {
  production: false,
  useHash: true,
  dataPath: './assets/dictionary_data.json'
};

/***/ }),

/***/ 7853:
/*!********************************************!*\
  !*** ./packages/mtd-mobile-ui/src/main.ts ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/platform-browser */ 436);
/* harmony import */ var _app_app_module__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./app/app.module */ 5451);


_angular_platform_browser__WEBPACK_IMPORTED_MODULE_1__.platformBrowser().bootstrapModule(_app_app_module__WEBPACK_IMPORTED_MODULE_0__.AppModule).catch(err => console.error(err));

/***/ }),

/***/ 9355:
/*!**************************************!*\
  !*** ./packages/search/src/index.ts ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DistanceCalculator: () => (/* reexport safe */ _lib_weighted_levenstein__WEBPACK_IMPORTED_MODULE_1__.DistanceCalculator),
/* harmony export */   Index: () => (/* reexport safe */ _lib_search__WEBPACK_IMPORTED_MODULE_0__.Index),
/* harmony export */   MTDSearch: () => (/* reexport safe */ _lib_search__WEBPACK_IMPORTED_MODULE_0__.MTDSearch),
/* harmony export */   TransducerAlgorithmTypes: () => (/* reexport safe */ _lib_factories__WEBPACK_IMPORTED_MODULE_3__.TransducerAlgorithmTypes),
/* harmony export */   constructSearchers: () => (/* reexport safe */ _lib_factories__WEBPACK_IMPORTED_MODULE_3__.constructSearchers),
/* harmony export */   constructTransducer: () => (/* reexport safe */ _lib_factories__WEBPACK_IMPORTED_MODULE_3__.constructTransducer),
/* harmony export */   create_normalization_function: () => (/* reexport safe */ _lib_search__WEBPACK_IMPORTED_MODULE_0__.create_normalization_function),
/* harmony export */   englishStemmer: () => (/* reexport safe */ _lib_search__WEBPACK_IMPORTED_MODULE_0__.englishStemmer),
/* harmony export */   returnTransducer: () => (/* reexport safe */ _lib_factories__WEBPACK_IMPORTED_MODULE_3__.returnTransducer),
/* harmony export */   sortResults: () => (/* reexport safe */ _lib_search__WEBPACK_IMPORTED_MODULE_0__.sortResults)
/* harmony export */ });
/* harmony import */ var _lib_search__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./lib/search */ 6991);
/* harmony import */ var _lib_weighted_levenstein__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./lib/weighted.levenstein */ 6011);
/* harmony import */ var _lib_mtd__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./lib/mtd */ 1064);
/* harmony import */ var _lib_factories__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./lib/factories */ 2845);





/***/ }),

/***/ 2845:
/*!**********************************************!*\
  !*** ./packages/search/src/lib/factories.ts ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TransducerAlgorithmTypes: () => (/* binding */ TransducerAlgorithmTypes),
/* harmony export */   constructSearchers: () => (/* binding */ constructSearchers),
/* harmony export */   constructTransducer: () => (/* binding */ constructTransducer),
/* harmony export */   returnTransducer: () => (/* binding */ returnTransducer)
/* harmony export */ });
/* harmony import */ var liblevenshtein__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! liblevenshtein */ 7630);
/* harmony import */ var liblevenshtein__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(liblevenshtein__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _search__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./search */ 6991);
/* harmony import */ var _weighted_levenstein__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./weighted.levenstein */ 6011);
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
//@ts-ignore



var TransducerAlgorithmTypes;
(function (TransducerAlgorithmTypes) {
  TransducerAlgorithmTypes["standard"] = "standard";
  TransducerAlgorithmTypes["merge_and_split"] = "merge_and_split";
  TransducerAlgorithmTypes["transposition"] = "transposition";
})(TransducerAlgorithmTypes || (TransducerAlgorithmTypes = {}));
function returnTransducer(searchType, index, config) {
  let transducer = null;
  if (searchType === 'liblevenstein_automata') {
    transducer = constructTransducer({
      terms: index
    });
  } else if (searchType === 'weighted_levenstein') {
    if (config) {
      transducer = new _weighted_levenstein__WEBPACK_IMPORTED_MODULE_2__.DistanceCalculator(config);
    } else {
      transducer = new _weighted_levenstein__WEBPACK_IMPORTED_MODULE_2__.DistanceCalculator({});
    }
  }
  return transducer;
}
function constructTransducer({
  terms,
  algorithm = TransducerAlgorithmTypes.standard,
  sort_candidates = true,
  case_insensitive_sort = true,
  include_distance = true,
  maximum_candidates = 10
}) {
  if (!Array.isArray(terms)) {
    terms = Object.keys(terms.data);
  }
  const builder = new liblevenshtein__WEBPACK_IMPORTED_MODULE_0__.Builder().dictionary(terms, false) // generate spelling candidates from unsorted completion_list
  .algorithm(algorithm) // use Levenshtein distance extended with transposition
  .sort_candidates(sort_candidates) // sort the spelling candidates before returning them
  .case_insensitive_sort(case_insensitive_sort) // ignore character-casing while sorting terms
  .include_distance(include_distance) // keep distances
  .maximum_candidates(maximum_candidates); // maximum number of candidates
  return builder.build();
}
function constructSearchers(mtdExportFormat) {
  // Load L1 Index
  const l1_index = new _search__WEBPACK_IMPORTED_MODULE_1__.Index({
    normalizeFunctionConfig: mtdExportFormat.config.l1_normalization_transducer,
    stemmerFunctionChoice: mtdExportFormat.config.l1_stemmer,
    data: mtdExportFormat.l1_index
  });
  // Create L1 Search Transducer
  const l1_transducer = returnTransducer(mtdExportFormat.config.l1_search_strategy ?? 'liblevenstein_automata', l1_index, mtdExportFormat.config.l1_search_config ?? undefined);
  const l1SubstitutionCosts = mtdExportFormat.config.l1_search_config?.substitutionCosts;
  const l2SubstitutionCosts = mtdExportFormat.config.l2_search_config?.substitutionCosts;
  let l1_tokens = mtdExportFormat.config.alphabet;
  if (l1SubstitutionCosts) {
    l1_tokens = [...l1_tokens, ...Object.keys(l1SubstitutionCosts)];
  }
  let l2_tokens = mtdExportFormat.config.alphabet; // TODO: This isn't really right, not sure how we should tokenize though
  if (l2SubstitutionCosts) {
    l2_tokens = [...l2_tokens, ...Object.keys(l2SubstitutionCosts)];
  }
  // Create L1 Search Object
  const l1_search = new _search__WEBPACK_IMPORTED_MODULE_1__.MTDSearch({
    transducer: l1_transducer,
    index: l1_index,
    searchType: mtdExportFormat.config.l1_search_strategy ?? 'liblevenstein_automata',
    tokens: l1_tokens
  });
  // Load L2 Index
  const l2_index = new _search__WEBPACK_IMPORTED_MODULE_1__.Index({
    normalizeFunctionConfig: mtdExportFormat.config.l2_normalization_transducer,
    stemmerFunctionChoice: mtdExportFormat.config.l2_stemmer,
    data: mtdExportFormat.l2_index
  });
  // Create L2 Search Transducer
  const l2_transducer = returnTransducer(mtdExportFormat.config.l2_search_strategy ?? 'liblevenstein_automata', l2_index, mtdExportFormat.config.l2_search_config ?? undefined);
  // Create L2 Search Object
  const l2_search = new _search__WEBPACK_IMPORTED_MODULE_1__.MTDSearch({
    transducer: l2_transducer,
    index: l2_index,
    searchType: mtdExportFormat.config.l2_search_strategy ?? 'liblevenstein_automata',
    tokens: l2_tokens
  });
  return [l1_search, l2_search];
}

/***/ }),

/***/ 1064:
/*!****************************************!*\
  !*** ./packages/search/src/lib/mtd.ts ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */


/***/ }),

/***/ 6991:
/*!*******************************************!*\
  !*** ./packages/search/src/lib/search.ts ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Index: () => (/* binding */ Index),
/* harmony export */   MTDSearch: () => (/* binding */ MTDSearch),
/* harmony export */   create_normalization_function: () => (/* binding */ create_normalization_function),
/* harmony export */   englishStemmer: () => (/* binding */ englishStemmer),
/* harmony export */   sortResults: () => (/* binding */ sortResults)
/* harmony export */ });
/* harmony import */ var snowball_stemmers__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! snowball-stemmers */ 387);
/* harmony import */ var snowball_stemmers__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(snowball_stemmers__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./utils */ 8570);


// From the MTD configuration for a normalization function, create a normalization function
// capable of lowercasing, unicode normalization, punctuation remove, and arbitrary replace rules.
function create_normalization_function(config) {
  const callables = [];
  if (config.lower) {
    callables.push(string => string.toLowerCase());
  }
  if (config.remove_combining_characters) {
    callables.push(text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, ''));
  }
  if (config.unicode_normalization && config.unicode_normalization !== 'none') {
    callables.push(text => text.normalize(config.unicode_normalization));
  }
  if (config.remove_punctuation) {
    const regex = new RegExp(config.remove_punctuation, 'g');
    callables.push(text => text.replace(regex, ''));
  }
  if (config.replace_rules) {
    const replace = text => {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      Object.entries(config.replace_rules).forEach(([k, v]) => {
        const regEx = new RegExp(k, 'g');
        text = text.replace(regEx, v);
      });
      return text;
    };
    callables.push(replace);
  }
  if (callables.length < 1) {
    return string => string;
  }
  return text => {
    callables.forEach(callable => {
      text = callable(text);
    });
    return text;
  };
}
const englishSnowballStemmer = (0,snowball_stemmers__WEBPACK_IMPORTED_MODULE_0__.newStemmer)('english');
function englishStemmer(term) {
  return englishSnowballStemmer.stem(term);
}
class Index {
  constructor({
    normalizeFunctionConfig = {
      lower: true,
      unicode_normalization: 'NFC',
      remove_punctuation: "[.,/#!$%^&?*';:{}=\\-_`~()]",
      replace_rules: {}
    },
    stemmerFunctionChoice = 'none',
    data
  }) {
    this.data = {};
    this.normalizeFunction = create_normalization_function(normalizeFunctionConfig);
    if (stemmerFunctionChoice === 'snowball_english') {
      this.stemmerFunction = englishSnowballStemmer.stem;
    } else {
      this.stemmerFunction = undefined;
    }
    this.data = data;
  }
}
function sortResults(results) {
  return results.sort((a, b) => {
    // Sort by Levenstein distance first
    const n = a[0] - b[0];
    if (n !== 0) {
      return n;
    }
    // Then by BM25 score
    return b[3] - a[3];
  });
}
class MTDSearch {
  constructor({
    transducer,
    index,
    searchType,
    tokens
  }) {
    this.index = index;
    this.indexTerms = Object.keys(this.index.data);
    this.transducer = transducer;
    this.searchType = searchType;
    this.tokens = tokens;
    if (this.tokens !== undefined) {
      const sortedTokens = [...this.tokens].sort((a, b) => b.length - a.length);
      const regex = new RegExp('(' + sortedTokens.join('|') + ')', 'g');
      this.tokenizer = str => str.split(regex);
    } else {
      this.tokenizer = undefined;
    }
  }
  combine_results(flatResults) {
    // But to calculate the average Lev distance and score we first create an object
    // This function only sums the Lev distances, so they need to be divided by the
    // number of query terms later
    const combinedResults = {};
    const docCounter = new _utils__WEBPACK_IMPORTED_MODULE_1__.Counter([]);
    for (const result of flatResults) {
      const term = result[0];
      const distance = result[1];
      const postings = Object.keys(this.index.data[term]);
      docCounter.update(postings);
      postings.forEach(posting => {
        // Merge results in a single object
        if (posting in combinedResults) {
          combinedResults[posting][0] += distance;
          combinedResults[posting][1] = combinedResults[posting][1].concat(this.index.data[term][posting].location);
          combinedResults[posting][2] += this.index.data[term][posting]['score']['total'];
        } else {
          combinedResults[posting] = [distance, this.index.data[term][posting].location, this.index.data[term][posting].score['total']];
        }
      });
    }
    return {
      combinedResults,
      docCounter
    };
  }
  search(query, maximum_edit_distance = 2, sort = false) {
    const splitQueryTerms = query.split(/\s+/);
    const matchSets = {};
    const results = splitQueryTerms.map(word => {
      // normalize
      word = this.index.normalizeFunction(word);
      // stem
      if (this.index.stemmerFunction !== undefined) {
        word = this.index.stemmerFunction(word);
      }
      if (this.searchType === 'weighted_levenstein') {
        if (this.tokenizer !== undefined) {
          word = this.tokenizer(word);
          return this.indexTerms.map(term => [term,
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          this.transducer.getEditDistance(word, this.tokenizer(term))]).filter(result => result[1] < maximum_edit_distance);
        } else {
          return this.indexTerms.map(term => [term, this.transducer.getEditDistance(word, term)]).filter(result => result[1] < maximum_edit_distance);
        }
      } else {
        return this.transducer.transduce(word, maximum_edit_distance);
      }
    });
    // create sets of document ids for each query term for multi-word queries
    results.forEach((word, i) => {
      matchSets[splitQueryTerms[i]] = new Set(word.map(x => Object.keys(this.index.data[x[0]])).flat());
    });
    // Flatten multi-query results
    const flatResults = results.flat();
    // Combine the results by averaging the edit distance and summing the BM25 scores
    const {
      combinedResults,
      docCounter
    } = this.combine_results(flatResults);
    // We return a list of Results
    const resultsArray = Object.keys(combinedResults).map(posting => {
      return [
      // if the doc was not found by any of the query terms, add an upper-bound default of the max edit distance + 1 for the
      // un-matched query terms and then average the results
      (combinedResults[posting][0] + Math.max(0, splitQueryTerms.length - docCounter.counter[posting]) * (maximum_edit_distance + 1)) / splitQueryTerms.length, posting, combinedResults[posting][1], combinedResults[posting][2]];
    });
    if (sort) {
      if (maximum_edit_distance === 0) {
        // if max edit distance is 0
        // just sort by score
        return resultsArray.sort((a, b) => b[3] - a[3]);
      } else {
        // Sort by Lev Distance first
        // then by BM25 score
        return sortResults(resultsArray);
      }
    } else {
      return resultsArray;
    }
  }
}

/***/ }),

/***/ 8570:
/*!******************************************!*\
  !*** ./packages/search/src/lib/utils.ts ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Counter: () => (/* binding */ Counter)
/* harmony export */ });
class Counter {
  constructor(array) {
    this.counter = {};
    this.add = val => {
      this.counter[val] = (this.counter[val] || 0) + 1;
    };
    this.update = array => {
      array.forEach(val => this.add(val));
    };
    this.update(array);
  }
}

/***/ }),

/***/ 6011:
/*!********************************************************!*\
  !*** ./packages/search/src/lib/weighted.levenstein.ts ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DistanceCalculator: () => (/* binding */ DistanceCalculator)
/* harmony export */ });
/**
 * weighted.levenstein.ts
 *
 * A simple Levenshtein distance calculator, except weighted such
 * that insertions at the beginning and deletions at the end cost less.
 *
 * AUTHOR: Pat Littell
 * AUTHOR: Converted to TypeScript Class by Aidan Pine and add specific weighting for substitutions
 * LAST UPDATED: 2023-08-10
 */
class DistanceCalculator {
  constructor({
    insertionCost = 1.0,
    deletionCost = 1.0,
    insertionAtBeginningCost = 0.5,
    deletionAtEndCost = 0.5,
    substitutionCosts = {},
    defaultSubstitutionCost = 1.0
  }) {
    this.insertionCost = insertionCost;
    this.deletionCost = deletionCost;
    this.insertionAtBeginningCost = insertionAtBeginningCost;
    this.deletionAtEndCost = deletionAtEndCost;
    this.substitutionCosts = substitutionCosts;
    this.defaultSubstitutionCost = defaultSubstitutionCost;
  }
  getSubstitutionCost(a_char, b_char) {
    if (a_char === b_char) {
      return 0;
    } else {
      return this.substitutionCosts[a_char]?.[b_char] ?? this.defaultSubstitutionCost;
    }
  }
  getEditDistance(a, b) {
    if (a.length === 0) {
      return b.length;
    }
    if (b.length === 0) {
      return a.length;
    }
    const matrix = [];
    let currentInsertionCost = 0;
    let currentDeletionCost = 0;
    let currentSubstitutionCost = 0;
    // increment along the first column of each row
    let i;
    for (i = 0; i <= b.length; i++) {
      matrix[i] = [i * this.insertionAtBeginningCost];
    }
    // increment each column in the first row
    let j;
    for (j = 0; j <= a.length; j++) {
      matrix[0][j] = j;
    }
    // Fill in the rest of the matrix
    for (i = 1; i <= b.length; i++) {
      for (j = 1; j <= a.length; j++) {
        currentInsertionCost = matrix[i][j - 1] + this.insertionCost;
        currentSubstitutionCost = matrix[i - 1][j - 1] + this.getSubstitutionCost(a[j - 1], b[i - 1]);
        currentDeletionCost = matrix[i - 1][j] + (j == a.length ? this.deletionAtEndCost : this.deletionCost);
        matrix[i][j] = Math.min(currentSubstitutionCost, Math.min(currentInsertionCost, currentDeletionCost));
      }
    }
    return matrix[b.length][a.length];
  }
  // Given a query <a> and a series of targets <bs>, return the least distance to any target
  getLeastEditDistance(a, bs) {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const that = this;
    return Math.min.apply(null, bs.map(function (b) {
      return that.getEditDistance(a, b);
    }));
  }
}

/***/ }),

/***/ 8996:
/*!******************************************************************************************************************************************!*\
  !*** ./node_modules/@ionic/core/dist/esm/ lazy ^\.\/.*\.entry\.js$ include: \.entry\.js$ exclude: \.system\.entry\.js$ namespace object ***!
  \******************************************************************************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var map = {
	"./ion-accordion_2.entry.js": [
		7518,
		"common",
		"node_modules_ionic_core_dist_esm_ion-accordion_2_entry_js"
	],
	"./ion-action-sheet.entry.js": [
		1981,
		"common",
		"node_modules_ionic_core_dist_esm_ion-action-sheet_entry_js"
	],
	"./ion-alert.entry.js": [
		1603,
		"common",
		"node_modules_ionic_core_dist_esm_ion-alert_entry_js"
	],
	"./ion-app_8.entry.js": [
		2273,
		"common",
		"node_modules_ionic_core_dist_esm_ion-app_8_entry_js"
	],
	"./ion-avatar_3.entry.js": [
		9642,
		"node_modules_ionic_core_dist_esm_ion-avatar_3_entry_js"
	],
	"./ion-back-button.entry.js": [
		2095,
		"common",
		"node_modules_ionic_core_dist_esm_ion-back-button_entry_js"
	],
	"./ion-backdrop.entry.js": [
		2335,
		"node_modules_ionic_core_dist_esm_ion-backdrop_entry_js"
	],
	"./ion-breadcrumb_2.entry.js": [
		8221,
		"common",
		"node_modules_ionic_core_dist_esm_ion-breadcrumb_2_entry_js"
	],
	"./ion-button_2.entry.js": [
		7184,
		"node_modules_ionic_core_dist_esm_ion-button_2_entry_js"
	],
	"./ion-card_5.entry.js": [
		8759,
		"node_modules_ionic_core_dist_esm_ion-card_5_entry_js"
	],
	"./ion-checkbox.entry.js": [
		4248,
		"node_modules_ionic_core_dist_esm_ion-checkbox_entry_js"
	],
	"./ion-chip.entry.js": [
		9863,
		"node_modules_ionic_core_dist_esm_ion-chip_entry_js"
	],
	"./ion-col_3.entry.js": [
		1769,
		"node_modules_ionic_core_dist_esm_ion-col_3_entry_js"
	],
	"./ion-datetime-button.entry.js": [
		2569,
		"default-node_modules_ionic_core_dist_esm_data-ae11fd43_js",
		"node_modules_ionic_core_dist_esm_ion-datetime-button_entry_js"
	],
	"./ion-datetime_3.entry.js": [
		6534,
		"default-node_modules_ionic_core_dist_esm_data-ae11fd43_js",
		"common",
		"node_modules_ionic_core_dist_esm_ion-datetime_3_entry_js"
	],
	"./ion-fab_3.entry.js": [
		5458,
		"common",
		"node_modules_ionic_core_dist_esm_ion-fab_3_entry_js"
	],
	"./ion-img.entry.js": [
		654,
		"node_modules_ionic_core_dist_esm_ion-img_entry_js"
	],
	"./ion-infinite-scroll_2.entry.js": [
		6034,
		"common",
		"node_modules_ionic_core_dist_esm_ion-infinite-scroll_2_entry_js"
	],
	"./ion-input-password-toggle.entry.js": [
		5196,
		"common",
		"node_modules_ionic_core_dist_esm_ion-input-password-toggle_entry_js"
	],
	"./ion-input.entry.js": [
		761,
		"default-node_modules_ionic_core_dist_esm_input_utils-09c71bc7_js-node_modules_ionic_core_dist-8b8a84",
		"common",
		"node_modules_ionic_core_dist_esm_ion-input_entry_js"
	],
	"./ion-item-option_3.entry.js": [
		6492,
		"common",
		"node_modules_ionic_core_dist_esm_ion-item-option_3_entry_js"
	],
	"./ion-item_8.entry.js": [
		9557,
		"common",
		"node_modules_ionic_core_dist_esm_ion-item_8_entry_js"
	],
	"./ion-loading.entry.js": [
		8353,
		"common",
		"node_modules_ionic_core_dist_esm_ion-loading_entry_js"
	],
	"./ion-menu_3.entry.js": [
		1024,
		"common",
		"node_modules_ionic_core_dist_esm_ion-menu_3_entry_js"
	],
	"./ion-modal.entry.js": [
		9160,
		"common",
		"node_modules_ionic_core_dist_esm_ion-modal_entry_js"
	],
	"./ion-nav_2.entry.js": [
		393,
		"node_modules_ionic_core_dist_esm_ion-nav_2_entry_js"
	],
	"./ion-picker-column-option.entry.js": [
		8442,
		"node_modules_ionic_core_dist_esm_ion-picker-column-option_entry_js"
	],
	"./ion-picker-column.entry.js": [
		3110,
		"common",
		"node_modules_ionic_core_dist_esm_ion-picker-column_entry_js"
	],
	"./ion-picker.entry.js": [
		5575,
		"node_modules_ionic_core_dist_esm_ion-picker_entry_js"
	],
	"./ion-popover.entry.js": [
		6772,
		"common",
		"node_modules_ionic_core_dist_esm_ion-popover_entry_js"
	],
	"./ion-progress-bar.entry.js": [
		4810,
		"node_modules_ionic_core_dist_esm_ion-progress-bar_entry_js"
	],
	"./ion-radio_2.entry.js": [
		4639,
		"common",
		"node_modules_ionic_core_dist_esm_ion-radio_2_entry_js"
	],
	"./ion-range.entry.js": [
		628,
		"common",
		"node_modules_ionic_core_dist_esm_ion-range_entry_js"
	],
	"./ion-refresher_2.entry.js": [
		852,
		"common",
		"node_modules_ionic_core_dist_esm_ion-refresher_2_entry_js"
	],
	"./ion-reorder_2.entry.js": [
		1479,
		"common",
		"node_modules_ionic_core_dist_esm_ion-reorder_2_entry_js"
	],
	"./ion-ripple-effect.entry.js": [
		4065,
		"node_modules_ionic_core_dist_esm_ion-ripple-effect_entry_js"
	],
	"./ion-route_4.entry.js": [
		7971,
		"node_modules_ionic_core_dist_esm_ion-route_4_entry_js"
	],
	"./ion-searchbar.entry.js": [
		3184,
		"common",
		"node_modules_ionic_core_dist_esm_ion-searchbar_entry_js"
	],
	"./ion-segment_2.entry.js": [
		469,
		"common",
		"node_modules_ionic_core_dist_esm_ion-segment_2_entry_js"
	],
	"./ion-select_3.entry.js": [
		8471,
		"common",
		"node_modules_ionic_core_dist_esm_ion-select_3_entry_js"
	],
	"./ion-spinner.entry.js": [
		388,
		"common",
		"node_modules_ionic_core_dist_esm_ion-spinner_entry_js"
	],
	"./ion-split-pane.entry.js": [
		2392,
		"node_modules_ionic_core_dist_esm_ion-split-pane_entry_js"
	],
	"./ion-tab-bar_2.entry.js": [
		6059,
		"common",
		"node_modules_ionic_core_dist_esm_ion-tab-bar_2_entry_js"
	],
	"./ion-tab_2.entry.js": [
		5427,
		"node_modules_ionic_core_dist_esm_ion-tab_2_entry_js"
	],
	"./ion-text.entry.js": [
		198,
		"node_modules_ionic_core_dist_esm_ion-text_entry_js"
	],
	"./ion-textarea.entry.js": [
		1735,
		"default-node_modules_ionic_core_dist_esm_input_utils-09c71bc7_js-node_modules_ionic_core_dist-8b8a84",
		"node_modules_ionic_core_dist_esm_ion-textarea_entry_js"
	],
	"./ion-toast.entry.js": [
		7510,
		"common",
		"node_modules_ionic_core_dist_esm_ion-toast_entry_js"
	],
	"./ion-toggle.entry.js": [
		5297,
		"common",
		"node_modules_ionic_core_dist_esm_ion-toggle_entry_js"
	]
};
function webpackAsyncContext(req) {
	if(!__webpack_require__.o(map, req)) {
		return Promise.resolve().then(() => {
			var e = new Error("Cannot find module '" + req + "'");
			e.code = 'MODULE_NOT_FOUND';
			throw e;
		});
	}

	var ids = map[req], id = ids[0];
	return Promise.all(ids.slice(1).map(__webpack_require__.e)).then(() => {
		return __webpack_require__(id);
	});
}
webpackAsyncContext.keys = () => (Object.keys(map));
webpackAsyncContext.id = 8996;
module.exports = webpackAsyncContext;

/***/ }),

/***/ 3199:
/*!*****************************************************************************************************************************************************!*\
  !*** ./node_modules/@stencil/core/internal/client/ lazy ^\.\/.*\.entry\.js.*$ include: \.entry\.js$ exclude: \.system\.entry\.js$ namespace object ***!
  \*****************************************************************************************************************************************************/
/***/ ((module) => {

function webpackEmptyAsyncContext(req) {
	// Here Promise.resolve().then() is used instead of new Promise() to prevent
	// uncaught exception popping up in devtools
	return Promise.resolve().then(() => {
		var e = new Error("Cannot find module '" + req + "'");
		e.code = 'MODULE_NOT_FOUND';
		throw e;
	});
}
webpackEmptyAsyncContext.keys = () => ([]);
webpackEmptyAsyncContext.resolve = webpackEmptyAsyncContext;
webpackEmptyAsyncContext.id = 3199;
module.exports = webpackEmptyAsyncContext;

/***/ })

},
/******/ __webpack_require__ => { // webpackRuntimeModules
/******/ var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
/******/ __webpack_require__.O(0, ["vendor"], () => (__webpack_exec__(7853)));
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=main.js.map