"use strict";
(self["webpackChunkmtd_mobile_ui"] = self["webpackChunkmtd_mobile_ui"] || []).push([["packages_mtd-mobile-ui_src_app_browse_browse_module_ts"],{

/***/ 6700:
/*!************************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/browse/browse-routing.module.ts ***!
  \************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   BrowsePageRoutingModule: () => (/* binding */ BrowsePageRoutingModule)
/* harmony export */ });
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/router */ 5072);
/* harmony import */ var _browse_page__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./browse.page */ 1286);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ 7580);




const routes = [{
  path: '',
  component: _browse_page__WEBPACK_IMPORTED_MODULE_0__.BrowsePage
}];
class BrowsePageRoutingModule {
  static #_ = this.ɵfac = function BrowsePageRoutingModule_Factory(t) {
    return new (t || BrowsePageRoutingModule)();
  };
  static #_2 = this.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineNgModule"]({
    type: BrowsePageRoutingModule
  });
  static #_3 = this.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineInjector"]({
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule.forChild(routes), _angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule]
  });
}
(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵsetNgModuleScope"](BrowsePageRoutingModule, {
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule],
    exports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__.RouterModule]
  });
})();

/***/ }),

/***/ 4925:
/*!****************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/browse/browse.module.ts ***!
  \****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   BrowsePageModule: () => (/* binding */ BrowsePageModule)
/* harmony export */ });
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/forms */ 4456);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _browse_routing_module__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./browse-routing.module */ 6700);
/* harmony import */ var _browse_page__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./browse.page */ 1286);
/* harmony import */ var _shared_shared_module__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../shared/shared.module */ 3023);
/* harmony import */ var _browse_service__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./browse.service */ 3518);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/core */ 7580);








class BrowsePageModule {
  static #_ = this.ɵfac = function BrowsePageModule_Factory(t) {
    return new (t || BrowsePageModule)();
  };
  static #_2 = this.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineNgModule"]({
    type: BrowsePageModule
  });
  static #_3 = this.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineInjector"]({
    providers: [_browse_service__WEBPACK_IMPORTED_MODULE_3__.BrowseService],
    imports: [_angular_common__WEBPACK_IMPORTED_MODULE_5__.CommonModule, _angular_forms__WEBPACK_IMPORTED_MODULE_6__.FormsModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_7__.IonicModule, _browse_routing_module__WEBPACK_IMPORTED_MODULE_0__.BrowsePageRoutingModule, _shared_shared_module__WEBPACK_IMPORTED_MODULE_2__.SharedModule]
  });
}
(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵsetNgModuleScope"](BrowsePageModule, {
    declarations: [_browse_page__WEBPACK_IMPORTED_MODULE_1__.BrowsePage],
    imports: [_angular_common__WEBPACK_IMPORTED_MODULE_5__.CommonModule, _angular_forms__WEBPACK_IMPORTED_MODULE_6__.FormsModule, _ionic_angular__WEBPACK_IMPORTED_MODULE_7__.IonicModule, _browse_routing_module__WEBPACK_IMPORTED_MODULE_0__.BrowsePageRoutingModule, _shared_shared_module__WEBPACK_IMPORTED_MODULE_2__.SharedModule]
  });
})();

/***/ }),

/***/ 1286:
/*!**************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/browse/browse.page.ts ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   BrowsePage: () => (/* binding */ BrowsePage)
/* harmony export */ });
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../data.service */ 5329);
/* harmony import */ var _browse_service__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./browse.service */ 3518);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ 7580);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/common */ 316);
/* harmony import */ var _ionic_angular__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @ionic/angular */ 1507);
/* harmony import */ var _shared_entry_list_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../shared/entry-list.component */ 7530);








const _c0 = a0 => ({
  start: a0
});
function BrowsePage_ion_select_option_14_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "ion-select-option");
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const category_r1 = ctx.$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtextInterpolate"](category_r1);
  }
}
function BrowsePage_ion_item_15_ion_select_option_3_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "ion-select-option");
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const letter_r4 = ctx.$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtextInterpolate"](letter_r4);
  }
}
function BrowsePage_ion_item_15_Template(rf, ctx) {
  if (rf & 1) {
    const _r2 = _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "ion-item")(1, "ion-select", 15);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipe"](2, "async");
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵlistener"]("ionChange", function BrowsePage_ion_item_15_Template_ion_select_ionChange_1_listener($event) {
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵrestoreView"](_r2);
      const ctx_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵresetView"](ctx_r2.handleLetterChange($event));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtemplate"](3, BrowsePage_ion_item_15_ion_select_option_3_Template, 2, 1, "ion-select-option", 6);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](4, "ion-toast", 16);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵlistener"]("didDismiss", function BrowsePage_ion_item_15_Template_ion_toast_didDismiss_4_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵrestoreView"](_r2);
      const ctx_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵresetView"](ctx_r2.letterNotFound = false);
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("value", _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipeBind1"](2, 4, ctx_r2.browseService.currentLetter$));
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("ngForOf", ctx_r2.displayLetters);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("isOpen", ctx_r2.letterNotFound)("duration", 5000);
  }
}
function BrowsePage_div_16_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "div", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelement"](1, "mtd-entry-list", 18);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const currentTen_r5 = ctx.ngIf;
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("entries", currentTen_r5);
  }
}
function BrowsePage_div_23_ion_title_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "ion-title");
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipe"](2, "async");
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    let tmp_3_0;
    const currentStart_r6 = _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵnextContext"]().ngIf;
    const ctx_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtextInterpolate3"]("Viewing ", currentStart_r6.start + 1, " to ", currentStart_r6.start + 10, " of ", (tmp_3_0 = _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipeBind1"](2, 3, ctx_r2.browseService.$currentEntries)) == null ? null : tmp_3_0.length, " Dictionary Entries");
  }
}
function BrowsePage_div_23_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "div", 19);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtemplate"](1, BrowsePage_div_23_ion_title_1_Template, 3, 5, "ion-title", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const currentStart_r6 = ctx.ngIf;
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("ngIf", currentStart_r6.start !== null);
  }
}
class BrowsePage {
  constructor(dataService, browseService) {
    this.dataService = dataService;
    this.browseService = browseService;
    this.$config = this.dataService.$config;
    this.displayLetters = [];
    this.categories = [];
    this.letterNotFound = false;
  }
  ngOnInit() {
    this.$dataHash = this.dataService.$entriesHash;
    this.dataService.$categories.subscribe(categories => this.categories = categories);
    this.dataService.$categorizedEntries.subscribe(entries => {
      if (entries['All'] !== undefined && entries['All'].length > 0) {
        this.browseService.$currentEntries.next(entries['All']);
      }
    });
    this.$config.subscribe(config => {
      if (config) {
        if (Array.isArray(config.alphabet)) {
          this.displayLetters = config.alphabet;
        } else {
          this.displayLetters = [...config.alphabet];
        }
      }
    });
  }
  handleLetterChange(letterEvent) {
    this.letterNotFound = false;
    const letterElement = letterEvent?.currentTarget;
    let found = false;
    for (const entry of this.browseService.$currentEntries.value) {
      if (entry.word.startsWith(letterElement.value)) {
        this.browseService.$currentIndexStart.next(this.browseService.$currentEntries.value.indexOf(entry));
        found = true;
        break;
      }
    }
    if (!found) {
      this.letterNotFound = true;
    }
  }
  handleCategoryChange(categoryEvent) {
    const categoryElement = categoryEvent?.currentTarget;
    this.browseService.$currentEntries.next(this.dataService.$categorizedEntries.value[categoryElement.value]);
    this.browseService.$currentIndexStart.next(0);
  }
  goBack() {
    this.browseService.$currentIndexStart.next(Math.max(0, this.browseService.$currentIndexStart.value - 10));
  }
  goForward() {
    this.browseService.$currentIndexStart.next(Math.min(this.browseService.$currentEntries.value.length - 10, this.browseService.$currentIndexStart.value + 10));
  }
  static #_ = this.ɵfac = function BrowsePage_Factory(t) {
    return new (t || BrowsePage)(_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdirectiveInject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService), _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdirectiveInject"](_browse_service__WEBPACK_IMPORTED_MODULE_1__.BrowseService));
  };
  static #_2 = this.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdefineComponent"]({
    type: BrowsePage,
    selectors: [["mtd-browse"]],
    decls: 28,
    vars: 12,
    consts: [[3, "translucent"], ["slot", "start"], [3, "fullscreen"], ["collapse", "condense"], ["size", "large"], ["label", "Select a Category", "placeholder", "All", 3, "ionChange"], [4, "ngFor", "ngForOf"], [4, "ngIf"], ["class", "entry-container", 4, "ngIf"], ["slot", "start", 1, "bar-buttons", "bar-buttons-ios"], [3, "click"], ["slot", "icon-only", "name", "chevron-back-outline", 1, "scroll"], ["class", "browse-info", 4, "ngIf"], ["slot", "end", 1, "bar-buttons", "bar-buttons-ios"], ["slot", "icon-only", "name", "chevron-forward-outline", 1, "scroll"], ["label", "Current Letter", 3, "ionChange", "value"], ["message", "Sorry, it doesn't look like there are any words that start with that letter", 3, "didDismiss", "isOpen", "duration"], [1, "entry-container"], [3, "entries"], [1, "browse-info"]],
    template: function BrowsePage_Template(rf, ctx) {
      if (rf & 1) {
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "ion-header", 0)(1, "ion-toolbar")(2, "ion-buttons", 1);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelement"](3, "ion-menu-button");
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](4, "ion-title");
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](5, "Browse");
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]()()();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](6, "ion-content", 2)(7, "ion-header", 3)(8, "ion-toolbar")(9, "ion-title", 4);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](10, "browse");
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]()()();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](11, "ion-list")(12, "ion-item")(13, "ion-select", 5);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵlistener"]("ionChange", function BrowsePage_Template_ion_select_ionChange_13_listener($event) {
          return ctx.handleCategoryChange($event);
        });
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtemplate"](14, BrowsePage_ion_select_option_14_Template, 2, 1, "ion-select-option", 6);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]()();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtemplate"](15, BrowsePage_ion_item_15_Template, 5, 6, "ion-item", 7);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtemplate"](16, BrowsePage_div_16_Template, 2, 1, "div", 8);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipe"](17, "async");
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](18, "ion-footer")(19, "ion-toolbar")(20, "ion-buttons", 9)(21, "ion-button", 10);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵlistener"]("click", function BrowsePage_Template_ion_button_click_21_listener() {
          return ctx.goBack();
        });
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelement"](22, "ion-icon", 11);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]()();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtemplate"](23, BrowsePage_div_23_Template, 2, 1, "div", 12);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipe"](24, "async");
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](25, "ion-buttons", 13)(26, "ion-button", 10);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵlistener"]("click", function BrowsePage_Template_ion_button_click_26_listener() {
          return ctx.goForward();
        });
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelement"](27, "ion-icon", 14);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]()()()();
      }
      if (rf & 2) {
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("translucent", true);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"](6);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("fullscreen", true);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"](8);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("ngForOf", ctx.categories);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("ngIf", ctx.displayLetters);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"]();
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("ngIf", _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipeBind1"](17, 6, ctx.browseService.currentTen$));
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"](7);
        _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("ngIf", _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpureFunction1"](10, _c0, _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵpipeBind1"](24, 8, ctx.browseService.$currentIndexStart)));
      }
    },
    dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_4__.NgForOf, _angular_common__WEBPACK_IMPORTED_MODULE_4__.NgIf, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonButton, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonButtons, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonContent, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonFooter, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonHeader, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonIcon, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonItem, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonList, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonMenuButton, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonSelect, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonSelectOption, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonTitle, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonToast, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.IonToolbar, _ionic_angular__WEBPACK_IMPORTED_MODULE_5__.SelectValueAccessor, _shared_entry_list_component__WEBPACK_IMPORTED_MODULE_2__.EntryListComponent, _angular_common__WEBPACK_IMPORTED_MODULE_4__.AsyncPipe],
    styles: [".browse-info[_ngcontent-%COMP%] {\n  margin: 0 auto;\n  text-align: center;\n}\n\n@media only screen and (max-width: 600px) {\n  .browse-info[_ngcontent-%COMP%] {\n    display: none;\n  }\n}\n\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3BhY2thZ2VzL210ZC1tb2JpbGUtdWkvc3JjL2FwcC9icm93c2UvYnJvd3NlLnBhZ2UuY3NzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBO0VBQ0UsY0FBYztFQUNkLGtCQUFrQjtBQUNwQjs7QUFFQTtFQUNFO0lBQ0UsYUFBYTtFQUNmO0FBQ0YiLCJzb3VyY2VzQ29udGVudCI6WyIuYnJvd3NlLWluZm8ge1xuICBtYXJnaW46IDAgYXV0bztcbiAgdGV4dC1hbGlnbjogY2VudGVyO1xufVxuXG5AbWVkaWEgb25seSBzY3JlZW4gYW5kIChtYXgtd2lkdGg6IDYwMHB4KSB7XG4gIC5icm93c2UtaW5mbyB7XG4gICAgZGlzcGxheTogbm9uZTtcbiAgfVxufVxuIl0sInNvdXJjZVJvb3QiOiIifQ== */"]
  });
}

/***/ }),

/***/ 3518:
/*!*****************************************************************!*\
  !*** ./packages/mtd-mobile-ui/src/app/browse/browse.service.ts ***!
  \*****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   BrowseService: () => (/* binding */ BrowseService)
/* harmony export */ });
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs */ 5797);
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! rxjs */ 9999);
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! rxjs */ 271);
/* harmony import */ var _data_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../data.service */ 5329);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/core */ 7580);




class BrowseService {
  constructor(dataService) {
    this.dataService = dataService;
    this.$config = this.dataService.$config;
    this.$currentEntries = new rxjs__WEBPACK_IMPORTED_MODULE_1__.BehaviorSubject([]);
    this.$currentIndexStart = new rxjs__WEBPACK_IMPORTED_MODULE_1__.BehaviorSubject(0);
    this.$manualTrigger = new rxjs__WEBPACK_IMPORTED_MODULE_1__.BehaviorSubject(null);
    this.currentTen$ = (0,rxjs__WEBPACK_IMPORTED_MODULE_2__.combineLatest)([this.$currentIndexStart, this.$currentEntries, this.$manualTrigger]).pipe((0,rxjs__WEBPACK_IMPORTED_MODULE_3__.map)(([start, entries, _]) => entries.slice(start, start + 10)));
    // Emit a combination of the start index and current entries any time either of them changes
    this.currentLetter$ = this.currentTen$.pipe((0,rxjs__WEBPACK_IMPORTED_MODULE_3__.map)(entries => {
      if (entries && this.$config?.value?.alphabet) {
        const firstNonOOVIndex = entries[0].sorting_form.filter(x => x < 10000)[0];
        return this.$config.value?.alphabet[firstNonOOVIndex];
      } else {
        return '';
      }
    }));
  }
  static #_ = this.ɵfac = function BrowseService_Factory(t) {
    return new (t || BrowseService)(_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵinject"](_data_service__WEBPACK_IMPORTED_MODULE_0__.DataService));
  };
  static #_2 = this.ɵprov = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineInjectable"]({
    token: BrowseService,
    factory: BrowseService.ɵfac,
    providedIn: 'root'
  });
}

/***/ })

}]);
//# sourceMappingURL=packages_mtd-mobile-ui_src_app_browse_browse_module_ts.js.map