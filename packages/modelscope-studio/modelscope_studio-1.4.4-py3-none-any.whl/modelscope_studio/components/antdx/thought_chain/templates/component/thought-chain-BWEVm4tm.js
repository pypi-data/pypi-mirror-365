import { i as en, a as ht, r as tn, Z as Ae, g as rn, c as X } from "./Index-BDCsf6Ht.js";
const P = window.ms_globals.React, x = window.ms_globals.React, Kr = window.ms_globals.React.isValidElement, qr = window.ms_globals.React.version, ee = window.ms_globals.React.useRef, Qr = window.ms_globals.React.useLayoutEffect, pe = window.ms_globals.React.useEffect, Yr = window.ms_globals.React.forwardRef, Zr = window.ms_globals.React.useState, Jr = window.ms_globals.React.useMemo, It = window.ms_globals.ReactDOM, mt = window.ms_globals.ReactDOM.createPortal, nn = window.ms_globals.internalContext.useContextPropsContext, $t = window.ms_globals.internalContext.ContextPropsProvider, on = window.ms_globals.createItemsContext.createItemsContext, sn = window.ms_globals.antd.ConfigProvider, pt = window.ms_globals.antd.theme, an = window.ms_globals.antd.Avatar, jt = window.ms_globals.antd.Typography, je = window.ms_globals.antdCssinjs.unit, et = window.ms_globals.antdCssinjs.token2CSSVar, zt = window.ms_globals.antdCssinjs.useStyleRegister, cn = window.ms_globals.antdCssinjs.useCSSVarRegister, ln = window.ms_globals.antdCssinjs.createTheme, un = window.ms_globals.antdCssinjs.useCacheToken, fn = window.ms_globals.antdIcons.LeftOutlined, dn = window.ms_globals.antdIcons.RightOutlined;
var mn = /\s/;
function hn(e) {
  for (var t = e.length; t-- && mn.test(e.charAt(t)); )
    ;
  return t;
}
var pn = /^\s+/;
function gn(e) {
  return e && e.slice(0, hn(e) + 1).replace(pn, "");
}
var Dt = NaN, vn = /^[-+]0x[0-9a-f]+$/i, yn = /^0b[01]+$/i, bn = /^0o[0-7]+$/i, Sn = parseInt;
function kt(e) {
  if (typeof e == "number")
    return e;
  if (en(e))
    return Dt;
  if (ht(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = ht(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = gn(e);
  var n = yn.test(e);
  return n || bn.test(e) ? Sn(e.slice(2), n ? 2 : 8) : vn.test(e) ? Dt : +e;
}
var tt = function() {
  return tn.Date.now();
}, xn = "Expected a function", Cn = Math.max, En = Math.min;
function _n(e, t, n) {
  var o, r, i, s, a, c, l = 0, d = !1, u = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(xn);
  t = kt(t) || 0, ht(n) && (d = !!n.leading, u = "maxWait" in n, i = u ? Cn(kt(n.maxWait) || 0, t) : i, f = "trailing" in n ? !!n.trailing : f);
  function m(p) {
    var M = o, T = r;
    return o = r = void 0, l = p, s = e.apply(T, M), s;
  }
  function v(p) {
    return l = p, a = setTimeout(S, t), d ? m(p) : s;
  }
  function g(p) {
    var M = p - c, T = p - l, R = t - M;
    return u ? En(R, i - T) : R;
  }
  function h(p) {
    var M = p - c, T = p - l;
    return c === void 0 || M >= t || M < 0 || u && T >= i;
  }
  function S() {
    var p = tt();
    if (h(p))
      return y(p);
    a = setTimeout(S, g(p));
  }
  function y(p) {
    return a = void 0, f && o ? m(p) : (o = r = void 0, s);
  }
  function _() {
    a !== void 0 && clearTimeout(a), l = 0, o = c = r = a = void 0;
  }
  function b() {
    return a === void 0 ? s : y(tt());
  }
  function w() {
    var p = tt(), M = h(p);
    if (o = arguments, r = this, c = p, M) {
      if (a === void 0)
        return v(c);
      if (u)
        return clearTimeout(a), a = setTimeout(S, t), m(c);
    }
    return a === void 0 && (a = setTimeout(S, t)), s;
  }
  return w.cancel = _, w.flush = b, w;
}
var pr = {
  exports: {}
}, De = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var wn = x, Tn = Symbol.for("react.element"), Mn = Symbol.for("react.fragment"), Pn = Object.prototype.hasOwnProperty, On = wn.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Rn = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function gr(e, t, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) Pn.call(t, o) && !Rn.hasOwnProperty(o) && (r[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) r[o] === void 0 && (r[o] = t[o]);
  return {
    $$typeof: Tn,
    type: e,
    key: i,
    ref: s,
    props: r,
    _owner: On.current
  };
}
De.Fragment = Mn;
De.jsx = gr;
De.jsxs = gr;
pr.exports = De;
var q = pr.exports;
const {
  SvelteComponent: Ln,
  assign: Ft,
  binding_callbacks: Nt,
  check_outros: An,
  children: vr,
  claim_element: yr,
  claim_space: In,
  component_subscribe: Ht,
  compute_slots: $n,
  create_slot: jn,
  detach: ae,
  element: br,
  empty: Vt,
  exclude_internal_props: Bt,
  get_all_dirty_from_scope: zn,
  get_slot_changes: Dn,
  group_outros: kn,
  init: Fn,
  insert_hydration: Ie,
  safe_not_equal: Nn,
  set_custom_element_data: Sr,
  space: Hn,
  transition_in: $e,
  transition_out: gt,
  update_slot_base: Vn
} = window.__gradio__svelte__internal, {
  beforeUpdate: Bn,
  getContext: Gn,
  onDestroy: Xn,
  setContext: Un
} = window.__gradio__svelte__internal;
function Gt(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), r = jn(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = br("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      t = yr(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = vr(t);
      r && r.l(s), s.forEach(ae), this.h();
    },
    h() {
      Sr(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      Ie(i, t, s), r && r.m(t, null), e[9](t), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && Vn(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? Dn(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : zn(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || ($e(r, i), n = !0);
    },
    o(i) {
      gt(r, i), n = !1;
    },
    d(i) {
      i && ae(t), r && r.d(i), e[9](null);
    }
  };
}
function Wn(e) {
  let t, n, o, r, i = (
    /*$$slots*/
    e[4].default && Gt(e)
  );
  return {
    c() {
      t = br("react-portal-target"), n = Hn(), i && i.c(), o = Vt(), this.h();
    },
    l(s) {
      t = yr(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), vr(t).forEach(ae), n = In(s), i && i.l(s), o = Vt(), this.h();
    },
    h() {
      Sr(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      Ie(s, t, a), e[8](t), Ie(s, n, a), i && i.m(s, a), Ie(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && $e(i, 1)) : (i = Gt(s), i.c(), $e(i, 1), i.m(o.parentNode, o)) : i && (kn(), gt(i, 1, 1, () => {
        i = null;
      }), An());
    },
    i(s) {
      r || ($e(i), r = !0);
    },
    o(s) {
      gt(i), r = !1;
    },
    d(s) {
      s && (ae(t), ae(n), ae(o)), e[8](null), i && i.d(s);
    }
  };
}
function Xt(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Kn(e, t, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = $n(i);
  let {
    svelteInit: c
  } = t;
  const l = Ae(Xt(t)), d = Ae();
  Ht(e, d, (b) => n(0, o = b));
  const u = Ae();
  Ht(e, u, (b) => n(1, r = b));
  const f = [], m = Gn("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h
  } = rn() || {}, S = c({
    parent: m,
    props: l,
    target: d,
    slot: u,
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h,
    onDestroy(b) {
      f.push(b);
    }
  });
  Un("$$ms-gr-react-wrapper", S), Bn(() => {
    l.set(Xt(t));
  }), Xn(() => {
    f.forEach((b) => b());
  });
  function y(b) {
    Nt[b ? "unshift" : "push"](() => {
      o = b, d.set(o);
    });
  }
  function _(b) {
    Nt[b ? "unshift" : "push"](() => {
      r = b, u.set(r);
    });
  }
  return e.$$set = (b) => {
    n(17, t = Ft(Ft({}, t), Bt(b))), "svelteInit" in b && n(5, c = b.svelteInit), "$$scope" in b && n(6, s = b.$$scope);
  }, t = Bt(t), [o, r, d, u, a, c, s, i, y, _];
}
class qn extends Ln {
  constructor(t) {
    super(), Fn(this, t, Kn, Wn, Nn, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Di
} = window.__gradio__svelte__internal, Ut = window.ms_globals.rerender, rt = window.ms_globals.tree;
function Qn(e, t = {}) {
  function n(o) {
    const r = Ae(), i = new qn({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? rt;
          return c.nodes = [...c.nodes, a], Ut({
            createPortal: mt,
            node: rt
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== r), Ut({
              createPortal: mt,
              node: rt
            });
          }), a;
        },
        ...o.props
      }
    });
    return r.set(i), i;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const Yn = "1.5.0";
function ue() {
  return ue = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (e[o] = n[o]);
    }
    return e;
  }, ue.apply(null, arguments);
}
function k(e) {
  "@babel/helpers - typeof";
  return k = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, k(e);
}
function Zn(e, t) {
  if (k(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(e, t);
    if (k(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function xr(e) {
  var t = Zn(e, "string");
  return k(t) == "symbol" ? t : t + "";
}
function E(e, t, n) {
  return (t = xr(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function Wt(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(e, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function C(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Wt(Object(n), !0).forEach(function(o) {
      E(e, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Wt(Object(n)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return e;
}
var Jn = `accept acceptCharset accessKey action allowFullScreen allowTransparency
    alt async autoComplete autoFocus autoPlay capture cellPadding cellSpacing challenge
    charSet checked classID className colSpan cols content contentEditable contextMenu
    controls coords crossOrigin data dateTime default defer dir disabled download draggable
    encType form formAction formEncType formMethod formNoValidate formTarget frameBorder
    headers height hidden high href hrefLang htmlFor httpEquiv icon id inputMode integrity
    is keyParams keyType kind label lang list loop low manifest marginHeight marginWidth max maxLength media
    mediaGroup method min minLength multiple muted name noValidate nonce open
    optimum pattern placeholder poster preload radioGroup readOnly rel required
    reversed role rowSpan rows sandbox scope scoped scrolling seamless selected
    shape size sizes span spellCheck src srcDoc srcLang srcSet start step style
    summary tabIndex target title type useMap value width wmode wrap`, eo = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, to = "".concat(Jn, " ").concat(eo).split(/[\s\n]+/), ro = "aria-", no = "data-";
function Kt(e, t) {
  return e.indexOf(t) === 0;
}
function Cr(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  t === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? n = {
    aria: !0
  } : n = C({}, t);
  var o = {};
  return Object.keys(e).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || Kt(r, ro)) || // Data
    n.data && Kt(r, no) || // Attr
    n.attr && to.includes(r)) && (o[r] = e[r]);
  }), o;
}
const oo = /* @__PURE__ */ x.createContext({}), io = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, so = (e) => {
  const t = x.useContext(oo);
  return x.useMemo(() => ({
    ...io,
    ...t[e]
  }), [t[e]]);
}, ao = "ant";
function vt() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = x.useContext(sn.ConfigContext);
  return {
    theme: r,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o
  };
}
function co(e) {
  if (Array.isArray(e)) return e;
}
function lo(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], c = !0, l = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        c = !1;
      } else for (; !(c = (o = i.call(n)).done) && (a.push(o.value), a.length !== t); c = !0) ;
    } catch (d) {
      l = !0, r = d;
    } finally {
      try {
        if (!c && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw r;
      }
    }
    return a;
  }
}
function qt(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, o = Array(t); n < t; n++) o[n] = e[n];
  return o;
}
function uo(e, t) {
  if (e) {
    if (typeof e == "string") return qt(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? qt(e, t) : void 0;
  }
}
function fo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function N(e, t) {
  return co(e) || lo(e, t) || uo(e, t) || fo();
}
function fe(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function Qt(e, t) {
  for (var n = 0; n < t.length; n++) {
    var o = t[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, xr(o.key), o);
  }
}
function de(e, t, n) {
  return t && Qt(e.prototype, t), n && Qt(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function se(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function yt(e, t) {
  return yt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, yt(e, t);
}
function ke(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && yt(e, t);
}
function ze(e) {
  return ze = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, ze(e);
}
function Er() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Er = function() {
    return !!e;
  })();
}
function mo(e, t) {
  if (t && (k(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return se(e);
}
function Fe(e) {
  var t = Er();
  return function() {
    var n, o = ze(e);
    if (t) {
      var r = ze(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return mo(this, n);
  };
}
var _r = /* @__PURE__ */ de(function e() {
  fe(this, e);
}), wr = "CALC_UNIT", ho = new RegExp(wr, "g");
function nt(e) {
  return typeof e == "number" ? "".concat(e).concat(wr) : e;
}
var po = /* @__PURE__ */ function(e) {
  ke(n, e);
  var t = Fe(n);
  function n(o, r) {
    var i;
    fe(this, n), i = t.call(this), E(se(i), "result", ""), E(se(i), "unitlessCssVar", void 0), E(se(i), "lowPriority", void 0);
    var s = k(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = nt(o) : s === "string" && (i.result = o), i;
  }
  return de(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(nt(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(nt(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " * ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " * ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " / ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " / ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(r) {
      return this.lowPriority || r ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(r) {
      var i = this, s = r || {}, a = s.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(l) {
        return i.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(ho, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(_r), go = /* @__PURE__ */ function(e) {
  ke(n, e);
  var t = Fe(n);
  function n(o) {
    var r;
    return fe(this, n), r = t.call(this), E(se(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return de(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result += r.result : typeof r == "number" && (this.result += r), this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result -= r.result : typeof r == "number" && (this.result -= r), this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return r instanceof n ? this.result *= r.result : typeof r == "number" && (this.result *= r), this;
    }
  }, {
    key: "div",
    value: function(r) {
      return r instanceof n ? this.result /= r.result : typeof r == "number" && (this.result /= r), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), n;
}(_r), vo = function(t, n) {
  var o = t === "css" ? po : go;
  return function(r) {
    return new o(r, n);
  };
}, Yt = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ge(e) {
  var t = P.useRef();
  t.current = e;
  var n = P.useCallback(function() {
    for (var o, r = arguments.length, i = new Array(r), s = 0; s < r; s++)
      i[s] = arguments[s];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return n;
}
function Ne() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var Zt = Ne() ? P.useLayoutEffect : P.useEffect, yo = function(t, n) {
  var o = P.useRef(!0);
  Zt(function() {
    return t(o.current);
  }, n), Zt(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, Jt = function(t, n) {
  yo(function(o) {
    if (!o)
      return t();
  }, n);
};
function ve(e) {
  var t = P.useRef(!1), n = P.useState(e), o = N(n, 2), r = o[0], i = o[1];
  P.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, c) {
    c && t.current || i(a);
  }
  return [r, s];
}
function ot(e) {
  return e !== void 0;
}
function bo(e, t) {
  var n = t || {}, o = n.defaultValue, r = n.value, i = n.onChange, s = n.postState, a = ve(function() {
    return ot(r) ? r : ot(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), c = N(a, 2), l = c[0], d = c[1], u = r !== void 0 ? r : l, f = s ? s(u) : u, m = ge(i), v = ve([u]), g = N(v, 2), h = g[0], S = g[1];
  Jt(function() {
    var _ = h[0];
    l !== _ && m(l, _);
  }, [h]), Jt(function() {
    ot(r) || d(r);
  }, [r]);
  var y = ge(function(_, b) {
    d(_, b), S([u], b);
  });
  return [f, y];
}
var Tr = {
  exports: {}
}, O = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Tt = Symbol.for("react.element"), Mt = Symbol.for("react.portal"), He = Symbol.for("react.fragment"), Ve = Symbol.for("react.strict_mode"), Be = Symbol.for("react.profiler"), Ge = Symbol.for("react.provider"), Xe = Symbol.for("react.context"), So = Symbol.for("react.server_context"), Ue = Symbol.for("react.forward_ref"), We = Symbol.for("react.suspense"), Ke = Symbol.for("react.suspense_list"), qe = Symbol.for("react.memo"), Qe = Symbol.for("react.lazy"), xo = Symbol.for("react.offscreen"), Mr;
Mr = Symbol.for("react.module.reference");
function U(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Tt:
        switch (e = e.type, e) {
          case He:
          case Be:
          case Ve:
          case We:
          case Ke:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case So:
              case Xe:
              case Ue:
              case Qe:
              case qe:
              case Ge:
                return e;
              default:
                return t;
            }
        }
      case Mt:
        return t;
    }
  }
}
O.ContextConsumer = Xe;
O.ContextProvider = Ge;
O.Element = Tt;
O.ForwardRef = Ue;
O.Fragment = He;
O.Lazy = Qe;
O.Memo = qe;
O.Portal = Mt;
O.Profiler = Be;
O.StrictMode = Ve;
O.Suspense = We;
O.SuspenseList = Ke;
O.isAsyncMode = function() {
  return !1;
};
O.isConcurrentMode = function() {
  return !1;
};
O.isContextConsumer = function(e) {
  return U(e) === Xe;
};
O.isContextProvider = function(e) {
  return U(e) === Ge;
};
O.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Tt;
};
O.isForwardRef = function(e) {
  return U(e) === Ue;
};
O.isFragment = function(e) {
  return U(e) === He;
};
O.isLazy = function(e) {
  return U(e) === Qe;
};
O.isMemo = function(e) {
  return U(e) === qe;
};
O.isPortal = function(e) {
  return U(e) === Mt;
};
O.isProfiler = function(e) {
  return U(e) === Be;
};
O.isStrictMode = function(e) {
  return U(e) === Ve;
};
O.isSuspense = function(e) {
  return U(e) === We;
};
O.isSuspenseList = function(e) {
  return U(e) === Ke;
};
O.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === He || e === Be || e === Ve || e === We || e === Ke || e === xo || typeof e == "object" && e !== null && (e.$$typeof === Qe || e.$$typeof === qe || e.$$typeof === Ge || e.$$typeof === Xe || e.$$typeof === Ue || e.$$typeof === Mr || e.getModuleId !== void 0);
};
O.typeOf = U;
Tr.exports = O;
var it = Tr.exports, Co = Symbol.for("react.element"), Eo = Symbol.for("react.transitional.element"), _o = Symbol.for("react.fragment");
function wo(e) {
  return (
    // Base object type
    e && k(e) === "object" && // React Element type
    (e.$$typeof === Co || e.$$typeof === Eo) && // React Fragment type
    e.type === _o
  );
}
var To = Number(qr.split(".")[0]), Mo = function(t, n) {
  typeof t == "function" ? t(n) : k(t) === "object" && t && "current" in t && (t.current = n);
}, Po = function(t) {
  var n, o;
  if (!t)
    return !1;
  if (Pr(t) && To >= 19)
    return !0;
  var r = it.isMemo(t) ? t.type.type : t.type;
  return !(typeof r == "function" && !((n = r.prototype) !== null && n !== void 0 && n.render) && r.$$typeof !== it.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== it.ForwardRef);
};
function Pr(e) {
  return /* @__PURE__ */ Kr(e) && !wo(e);
}
var Oo = function(t) {
  if (t && Pr(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function er(e, t, n, o) {
  var r = C({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var c = N(a, 2), l = c[0], d = c[1];
      if (r != null && r[l] || r != null && r[d]) {
        var u;
        (u = r[d]) !== null && u !== void 0 || (r[d] = r == null ? void 0 : r[l]);
      }
    });
  }
  var s = C(C({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Or = typeof CSSINJS_STATISTIC < "u", bt = !0;
function Pt() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Or)
    return Object.assign.apply(Object, [{}].concat(t));
  bt = !1;
  var o = {};
  return t.forEach(function(r) {
    if (k(r) === "object") {
      var i = Object.keys(r);
      i.forEach(function(s) {
        Object.defineProperty(o, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return r[s];
          }
        });
      });
    }
  }), bt = !0, o;
}
var tr = {};
function Ro() {
}
var Lo = function(t) {
  var n, o = t, r = Ro;
  return Or && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (bt) {
        var c;
        (c = n) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var c;
    tr[s] = {
      global: Array.from(n),
      component: C(C({}, (c = tr[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function rr(e, t, n) {
  if (typeof n == "function") {
    var o;
    return n(Pt(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function Ao(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return je(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return je(i);
      }).join(","), ")");
    }
  };
}
var Io = 1e3 * 60 * 10, $o = /* @__PURE__ */ function() {
  function e() {
    fe(this, e), E(this, "map", /* @__PURE__ */ new Map()), E(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), E(this, "nextID", 0), E(this, "lastAccessBeat", /* @__PURE__ */ new Map()), E(this, "accessBeat", 0);
  }
  return de(e, [{
    key: "set",
    value: function(n, o) {
      this.clear();
      var r = this.getCompositeKey(n);
      this.map.set(r, o), this.lastAccessBeat.set(r, Date.now());
    }
  }, {
    key: "get",
    value: function(n) {
      var o = this.getCompositeKey(n), r = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, r;
    }
  }, {
    key: "getCompositeKey",
    value: function(n) {
      var o = this, r = n.map(function(i) {
        return i && k(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(k(i), "_").concat(i);
      });
      return r.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(n) {
      if (this.objectIDMap.has(n))
        return this.objectIDMap.get(n);
      var o = this.nextID;
      return this.objectIDMap.set(n, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var n = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(r, i) {
          o - r > Io && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), nr = new $o();
function jo(e, t) {
  return x.useMemo(function() {
    var n = nr.get(t);
    if (n)
      return n;
    var o = e();
    return nr.set(t, o), o;
  }, t);
}
var zo = function() {
  return {};
};
function Do(e) {
  var t = e.useCSP, n = t === void 0 ? zo : t, o = e.useToken, r = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function c(f, m, v, g) {
    var h = Array.isArray(f) ? f[0] : f;
    function S(T) {
      return "".concat(String(h)).concat(T.slice(0, 1).toUpperCase()).concat(T.slice(1));
    }
    var y = (g == null ? void 0 : g.unitless) || {}, _ = typeof a == "function" ? a(f) : {}, b = C(C({}, _), {}, E({}, S("zIndexPopup"), !0));
    Object.keys(y).forEach(function(T) {
      b[S(T)] = y[T];
    });
    var w = C(C({}, g), {}, {
      unitless: b,
      prefixToken: S
    }), p = d(f, m, v, w), M = l(h, v, w);
    return function(T) {
      var R = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : T, L = p(T, R), A = N(L, 2), I = A[1], $ = M(R), j = N($, 2), z = j[0], V = j[1];
      return [z, I, V];
    };
  }
  function l(f, m, v) {
    var g = v.unitless, h = v.injectStyle, S = h === void 0 ? !0 : h, y = v.prefixToken, _ = v.ignore, b = function(M) {
      var T = M.rootCls, R = M.cssVar, L = R === void 0 ? {} : R, A = o(), I = A.realToken;
      return cn({
        path: [f],
        prefix: L.prefix,
        key: L.key,
        unitless: g,
        ignore: _,
        token: I,
        scope: T
      }, function() {
        var $ = rr(f, I, m), j = er(f, I, $, {
          deprecatedTokens: v == null ? void 0 : v.deprecatedTokens
        });
        return Object.keys($).forEach(function(z) {
          j[y(z)] = j[z], delete j[z];
        }), j;
      }), null;
    }, w = function(M) {
      var T = o(), R = T.cssVar;
      return [function(L) {
        return S && R ? /* @__PURE__ */ x.createElement(x.Fragment, null, /* @__PURE__ */ x.createElement(b, {
          rootCls: M,
          cssVar: R,
          component: f
        }), L) : L;
      }, R == null ? void 0 : R.key];
    };
    return w;
  }
  function d(f, m, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = Array.isArray(f) ? f : [f, f], S = N(h, 1), y = S[0], _ = h.join("-"), b = e.layer || {
      name: "antd"
    };
    return function(w) {
      var p = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : w, M = o(), T = M.theme, R = M.realToken, L = M.hashId, A = M.token, I = M.cssVar, $ = r(), j = $.rootPrefixCls, z = $.iconPrefixCls, V = n(), te = I ? "css" : "js", Z = jo(function() {
        var G = /* @__PURE__ */ new Set();
        return I && Object.keys(g.unitless || {}).forEach(function(ne) {
          G.add(et(ne, I.prefix)), G.add(et(ne, Yt(y, I.prefix)));
        }), vo(te, G);
      }, [te, y, I == null ? void 0 : I.prefix]), ye = Ao(te), be = ye.max, B = ye.min, re = {
        theme: T,
        token: A,
        hashId: L,
        nonce: function() {
          return V.nonce;
        },
        clientOnly: g.clientOnly,
        layer: b,
        // antd is always at top of styles
        order: g.order || -999
      };
      typeof i == "function" && zt(C(C({}, re), {}, {
        clientOnly: !1,
        path: ["Shared", j]
      }), function() {
        return i(A, {
          prefix: {
            rootPrefixCls: j,
            iconPrefixCls: z
          },
          csp: V
        });
      });
      var me = zt(C(C({}, re), {}, {
        path: [_, w, z]
      }), function() {
        if (g.injectStyle === !1)
          return [];
        var G = Lo(A), ne = G.token, Se = G.flush, Q = rr(y, R, v), Ye = ".".concat(w), xe = er(y, R, Q, {
          deprecatedTokens: g.deprecatedTokens
        });
        I && Q && k(Q) === "object" && Object.keys(Q).forEach(function(_e) {
          Q[_e] = "var(".concat(et(_e, Yt(y, I.prefix)), ")");
        });
        var Ce = Pt(ne, {
          componentCls: Ye,
          prefixCls: w,
          iconCls: ".".concat(z),
          antCls: ".".concat(j),
          calc: Z,
          // @ts-ignore
          max: be,
          // @ts-ignore
          min: B
        }, I ? Q : xe), Ee = m(Ce, {
          hashId: L,
          prefixCls: w,
          rootPrefixCls: j,
          iconPrefixCls: z
        });
        Se(y, xe);
        var oe = typeof s == "function" ? s(Ce, w, p, g.resetFont) : null;
        return [g.resetStyle === !1 ? null : oe, Ee];
      });
      return [me, L];
    };
  }
  function u(f, m, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = d(f, m, v, C({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, g)), S = function(_) {
      var b = _.prefixCls, w = _.rootCls, p = w === void 0 ? b : w;
      return h(b, p), null;
    };
    return S;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: u,
    genComponentStyleHook: d
  };
}
const ko = {
  blue: "#1677FF",
  purple: "#722ED1",
  cyan: "#13C2C2",
  green: "#52C41A",
  magenta: "#EB2F96",
  /**
   * @deprecated Use magenta instead
   */
  pink: "#EB2F96",
  red: "#F5222D",
  orange: "#FA8C16",
  yellow: "#FADB14",
  volcano: "#FA541C",
  geekblue: "#2F54EB",
  gold: "#FAAD14",
  lime: "#A0D911"
}, Fo = Object.assign(Object.assign({}, ko), {
  // Color
  colorPrimary: "#1677ff",
  colorSuccess: "#52c41a",
  colorWarning: "#faad14",
  colorError: "#ff4d4f",
  colorInfo: "#1677ff",
  colorLink: "",
  colorTextBase: "",
  colorBgBase: "",
  // Font
  fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
'Noto Color Emoji'`,
  fontFamilyCode: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace",
  fontSize: 14,
  // Line
  lineWidth: 1,
  lineType: "solid",
  // Motion
  motionUnit: 0.1,
  motionBase: 0,
  motionEaseOutCirc: "cubic-bezier(0.08, 0.82, 0.17, 1)",
  motionEaseInOutCirc: "cubic-bezier(0.78, 0.14, 0.15, 0.86)",
  motionEaseOut: "cubic-bezier(0.215, 0.61, 0.355, 1)",
  motionEaseInOut: "cubic-bezier(0.645, 0.045, 0.355, 1)",
  motionEaseOutBack: "cubic-bezier(0.12, 0.4, 0.29, 1.46)",
  motionEaseInBack: "cubic-bezier(0.71, -0.46, 0.88, 0.6)",
  motionEaseInQuint: "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
  motionEaseOutQuint: "cubic-bezier(0.23, 1, 0.32, 1)",
  // Radius
  borderRadius: 6,
  // Size
  sizeUnit: 4,
  sizeStep: 4,
  sizePopupArrow: 16,
  // Control Base
  controlHeight: 32,
  // zIndex
  zIndexBase: 0,
  zIndexPopupBase: 1e3,
  // Image
  opacityImage: 1,
  // Wireframe
  wireframe: !1,
  // Motion
  motion: !0
}), D = Math.round;
function st(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = t(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const or = (e, t, n) => n === 0 ? e : e / 100;
function he(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class Y {
  constructor(t) {
    E(this, "isValid", !0), E(this, "r", 0), E(this, "g", 0), E(this, "b", 0), E(this, "a", 1), E(this, "_h", void 0), E(this, "_s", void 0), E(this, "_l", void 0), E(this, "_v", void 0), E(this, "_max", void 0), E(this, "_min", void 0), E(this, "_brightness", void 0);
    function n(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (t instanceof Y)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = he(t.r), this.g = he(t.g), this.b = he(t.b), this.a = typeof t.a == "number" ? he(t.a, 1) : 1;
    else if (n("hsl"))
      this.fromHsl(t);
    else if (n("hsv"))
      this.fromHsv(t);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(t));
  }
  // ======================= Setter =======================
  setR(t) {
    return this._sc("r", t);
  }
  setG(t) {
    return this._sc("g", t);
  }
  setB(t) {
    return this._sc("b", t);
  }
  setA(t) {
    return this._sc("a", t, 1);
  }
  setHue(t) {
    const n = this.toHsv();
    return n.h = t, this._c(n);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function t(i) {
      const s = i / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const n = t(this.r), o = t(this.g), r = t(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = D(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._s = 0 : this._s = t / this.getMax();
    }
    return this._s;
  }
  getLightness() {
    return typeof this._l > "u" && (this._l = (this.getMax() + this.getMin()) / 510), this._l;
  }
  getValue() {
    return typeof this._v > "u" && (this._v = this.getMax() / 255), this._v;
  }
  /**
   * Returns the perceived brightness of the color, from 0-255.
   * Note: this is not the b of HSB
   * @see http://www.w3.org/TR/AERT#color-contrast
   */
  getBrightness() {
    return typeof this._brightness > "u" && (this._brightness = (this.r * 299 + this.g * 587 + this.b * 114) / 1e3), this._brightness;
  }
  // ======================== Func ========================
  darken(t = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() - t / 100;
    return r < 0 && (r = 0), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  lighten(t = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() + t / 100;
    return r > 1 && (r = 1), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, n = 50) {
    const o = this._c(t), r = n / 100, i = (a) => (o[a] - this[a]) * r + this[a], s = {
      r: D(i("r")),
      g: D(i("g")),
      b: D(i("b")),
      a: D(i("a") * 100) / 100
    };
    return this._c(s);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(t = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, t);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(t = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, t);
  }
  onBackground(t) {
    const n = this._c(t), o = this.a + n.a * (1 - this.a), r = (i) => D((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
    return this._c({
      r: r("r"),
      g: r("g"),
      b: r("b"),
      a: o
    });
  }
  // ======================= Status =======================
  isDark() {
    return this.getBrightness() < 128;
  }
  isLight() {
    return this.getBrightness() >= 128;
  }
  // ======================== MISC ========================
  equals(t) {
    return this.r === t.r && this.g === t.g && this.b === t.b && this.a === t.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let t = "#";
    const n = (this.r || 0).toString(16);
    t += n.length === 2 ? n : "0" + n;
    const o = (this.g || 0).toString(16);
    t += o.length === 2 ? o : "0" + o;
    const r = (this.b || 0).toString(16);
    if (t += r.length === 2 ? r : "0" + r, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = D(this.a * 255).toString(16);
      t += i.length === 2 ? i : "0" + i;
    }
    return t;
  }
  /** CSS support color pattern */
  toHsl() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      l: this.getLightness(),
      a: this.a
    };
  }
  /** CSS support color pattern */
  toHslString() {
    const t = this.getHue(), n = D(this.getSaturation() * 100), o = D(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${n}%,${o}%,${this.a})` : `hsl(${t},${n}%,${o}%)`;
  }
  /** Same as toHsb */
  toHsv() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      v: this.getValue(),
      a: this.a
    };
  }
  toRgb() {
    return {
      r: this.r,
      g: this.g,
      b: this.b,
      a: this.a
    };
  }
  toRgbString() {
    return this.a !== 1 ? `rgba(${this.r},${this.g},${this.b},${this.a})` : `rgb(${this.r},${this.g},${this.b})`;
  }
  toString() {
    return this.toRgbString();
  }
  // ====================== Privates ======================
  /** Return a new FastColor object with one channel changed */
  _sc(t, n, o) {
    const r = this.clone();
    return r[t] = he(n, o), r;
  }
  _c(t) {
    return new this.constructor(t);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(t) {
    const n = t.replace("#", "");
    function o(r, i) {
      return parseInt(n[r] + n[i || r], 16);
    }
    n.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = n[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = n[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: n,
    l: o,
    a: r
  }) {
    if (this._h = t % 360, this._s = n, this._l = o, this.a = typeof r == "number" ? r : 1, n <= 0) {
      const f = D(o * 255);
      this.r = f, this.g = f, this.b = f;
    }
    let i = 0, s = 0, a = 0;
    const c = t / 60, l = (1 - Math.abs(2 * o - 1)) * n, d = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = l, s = d) : c >= 1 && c < 2 ? (i = d, s = l) : c >= 2 && c < 3 ? (s = l, a = d) : c >= 3 && c < 4 ? (s = d, a = l) : c >= 4 && c < 5 ? (i = d, a = l) : c >= 5 && c < 6 && (i = l, a = d);
    const u = o - l / 2;
    this.r = D((i + u) * 255), this.g = D((s + u) * 255), this.b = D((a + u) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: o,
    a: r
  }) {
    this._h = t % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = D(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = t / 60, a = Math.floor(s), c = s - a, l = D(o * (1 - n) * 255), d = D(o * (1 - n * c) * 255), u = D(o * (1 - n * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = u, this.b = l;
        break;
      case 1:
        this.r = d, this.b = l;
        break;
      case 2:
        this.r = l, this.b = u;
        break;
      case 3:
        this.r = l, this.g = d;
        break;
      case 4:
        this.r = u, this.g = l;
        break;
      case 5:
      default:
        this.g = l, this.b = d;
        break;
    }
  }
  fromHsvString(t) {
    const n = st(t, or);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = st(t, or);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = st(t, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? D(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function at(e) {
  return e >= 0 && e <= 255;
}
function Me(e, t) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new Y(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: c
  } = new Y(t).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const d = Math.round((n - s * (1 - l)) / l), u = Math.round((o - a * (1 - l)) / l), f = Math.round((r - c * (1 - l)) / l);
    if (at(d) && at(u) && at(f))
      return new Y({
        r: d,
        g: u,
        b: f,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new Y({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var No = function(e, t) {
  var n = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (n[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(e); r < o.length; r++)
    t.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[r]) && (n[o[r]] = e[o[r]]);
  return n;
};
function Ho(e) {
  const {
    override: t
  } = e, n = No(e, ["override"]), o = Object.assign({}, t);
  Object.keys(Fo).forEach((f) => {
    delete o[f];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, c = 992, l = 1200, d = 1600;
  if (r.motion === !1) {
    const f = "0s";
    r.motionDurationFast = f, r.motionDurationMid = f, r.motionDurationSlow = f;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: Me(r.colorBorderSecondary, r.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: r.colorTextQuaternary,
    colorTextDisabled: r.colorTextQuaternary,
    colorTextHeading: r.colorText,
    colorTextLabel: r.colorTextSecondary,
    colorTextDescription: r.colorTextTertiary,
    colorTextLightSolid: r.colorWhite,
    colorHighlight: r.colorError,
    colorBgTextHover: r.colorFillSecondary,
    colorBgTextActive: r.colorFill,
    colorIcon: r.colorTextTertiary,
    colorIconHover: r.colorText,
    colorErrorOutline: Me(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: Me(r.colorWarningBg, r.colorBgContainer),
    // Font
    fontSizeIcon: r.fontSizeSM,
    // Line
    lineWidthFocus: r.lineWidth * 3,
    // Control
    lineWidth: r.lineWidth,
    controlOutlineWidth: r.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: r.controlHeight / 2,
    controlItemBgHover: r.colorFillTertiary,
    controlItemBgActive: r.colorPrimaryBg,
    controlItemBgActiveHover: r.colorPrimaryBgHover,
    controlItemBgActiveDisabled: r.colorFill,
    controlTmpOutline: r.colorFillQuaternary,
    controlOutline: Me(r.colorPrimaryBg, r.colorBgContainer),
    lineType: r.lineType,
    borderRadius: r.borderRadius,
    borderRadiusXS: r.borderRadiusXS,
    borderRadiusSM: r.borderRadiusSM,
    borderRadiusLG: r.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: r.sizeXXS,
    paddingXS: r.sizeXS,
    paddingSM: r.sizeSM,
    padding: r.size,
    paddingMD: r.sizeMD,
    paddingLG: r.sizeLG,
    paddingXL: r.sizeXL,
    paddingContentHorizontalLG: r.sizeLG,
    paddingContentVerticalLG: r.sizeMS,
    paddingContentHorizontal: r.sizeMS,
    paddingContentVertical: r.sizeSM,
    paddingContentHorizontalSM: r.size,
    paddingContentVerticalSM: r.sizeXS,
    marginXXS: r.sizeXXS,
    marginXS: r.sizeXS,
    marginSM: r.sizeSM,
    margin: r.size,
    marginMD: r.sizeMD,
    marginLG: r.sizeLG,
    marginXL: r.sizeXL,
    marginXXL: r.sizeXXL,
    boxShadow: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowSecondary: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTertiary: `
      0 1px 2px 0 rgba(0, 0, 0, 0.03),
      0 1px 6px -1px rgba(0, 0, 0, 0.02),
      0 2px 4px 0 rgba(0, 0, 0, 0.02)
    `,
    screenXS: i,
    screenXSMin: i,
    screenXSMax: s - 1,
    screenSM: s,
    screenSMMin: s,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: c - 1,
    screenLG: c,
    screenLGMin: c,
    screenLGMax: l - 1,
    screenXL: l,
    screenXLMin: l,
    screenXLMax: d - 1,
    screenXXL: d,
    screenXXLMin: d,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new Y("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new Y("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new Y("rgba(0, 0, 0, 0.09)").toRgbString()}
    `,
    boxShadowDrawerRight: `
      -6px 0 16px 0 rgba(0, 0, 0, 0.08),
      -3px 0 6px -4px rgba(0, 0, 0, 0.12),
      -9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerLeft: `
      6px 0 16px 0 rgba(0, 0, 0, 0.08),
      3px 0 6px -4px rgba(0, 0, 0, 0.12),
      9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerUp: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerDown: `
      0 -6px 16px 0 rgba(0, 0, 0, 0.08),
      0 -3px 6px -4px rgba(0, 0, 0, 0.12),
      0 -9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTabsOverflowLeft: "inset 10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowRight: "inset -10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowTop: "inset 0 10px 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowBottom: "inset 0 -10px 8px -8px rgba(0, 0, 0, 0.08)"
  }), o);
}
const Vo = {
  lineHeight: !0,
  lineHeightSM: !0,
  lineHeightLG: !0,
  lineHeightHeading1: !0,
  lineHeightHeading2: !0,
  lineHeightHeading3: !0,
  lineHeightHeading4: !0,
  lineHeightHeading5: !0,
  opacityLoading: !0,
  fontWeightStrong: !0,
  zIndexPopupBase: !0,
  zIndexBase: !0,
  opacityImage: !0
}, Bo = {
  size: !0,
  sizeSM: !0,
  sizeLG: !0,
  sizeMD: !0,
  sizeXS: !0,
  sizeXXS: !0,
  sizeMS: !0,
  sizeXL: !0,
  sizeXXL: !0,
  sizeUnit: !0,
  sizeStep: !0,
  motionBase: !0,
  motionUnit: !0
}, Go = ln(pt.defaultAlgorithm), Xo = {
  screenXS: !0,
  screenXSMin: !0,
  screenXSMax: !0,
  screenSM: !0,
  screenSMMin: !0,
  screenSMMax: !0,
  screenMD: !0,
  screenMDMin: !0,
  screenMDMax: !0,
  screenLG: !0,
  screenLGMin: !0,
  screenLGMax: !0,
  screenXL: !0,
  screenXLMin: !0,
  screenXLMax: !0,
  screenXXL: !0,
  screenXXLMin: !0
}, Rr = (e, t, n) => {
  const o = n.getDerivativeToken(e), {
    override: r,
    ...i
  } = t;
  let s = {
    ...o,
    override: r
  };
  return s = Ho(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: l,
      ...d
    } = c;
    let u = d;
    l && (u = Rr({
      ...s,
      ...d
    }, {
      override: d
    }, l)), s[a] = u;
  }), s;
};
function Uo() {
  const {
    token: e,
    hashed: t,
    theme: n = Go,
    override: o,
    cssVar: r
  } = x.useContext(pt._internalContext), [i, s, a] = un(n, [pt.defaultSeed, e], {
    salt: `${Yn}-${t || ""}`,
    override: o,
    getComputedToken: Rr,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: Vo,
      ignore: Bo,
      preserve: Xo
    }
  });
  return [n, a, t ? s : "", i, r];
}
const {
  genStyleHooks: Wo
} = Do({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = vt();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, o, r] = Uo();
    return {
      theme: e,
      realToken: t,
      hashId: n,
      token: o,
      cssVar: r
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = vt();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function ir(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function Ko(e) {
  return e && k(e) === "object" && ir(e.nativeElement) ? e.nativeElement : ir(e) ? e : null;
}
function qo(e) {
  var t = Ko(e);
  if (t)
    return t;
  if (e instanceof x.Component) {
    var n;
    return (n = It.findDOMNode) === null || n === void 0 ? void 0 : n.call(It, e);
  }
  return null;
}
function Qo(e, t) {
  if (e == null) return {};
  var n = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    n[o] = e[o];
  }
  return n;
}
function sr(e, t) {
  if (e == null) return {};
  var n, o, r = Qo(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) n = i[o], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (r[n] = e[n]);
  }
  return r;
}
var Yo = /* @__PURE__ */ P.createContext({}), Zo = /* @__PURE__ */ function(e) {
  ke(n, e);
  var t = Fe(n);
  function n() {
    return fe(this, n), t.apply(this, arguments);
  }
  return de(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(P.Component);
function Jo(e) {
  var t = P.useReducer(function(a) {
    return a + 1;
  }, 0), n = N(t, 2), o = n[1], r = P.useRef(e), i = ge(function() {
    return r.current;
  }), s = ge(function(a) {
    r.current = typeof a == "function" ? a(r.current) : a, o();
  });
  return [i, s];
}
var J = "none", Pe = "appear", Oe = "enter", Re = "leave", ar = "none", W = "prepare", ce = "start", le = "active", Ot = "end", Lr = "prepared";
function cr(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function ei(e, t) {
  var n = {
    animationend: cr("Animation", "AnimationEnd"),
    transitionend: cr("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var ti = ei(Ne(), typeof window < "u" ? window : {}), Ar = {};
if (Ne()) {
  var ri = document.createElement("div");
  Ar = ri.style;
}
var Le = {};
function Ir(e) {
  if (Le[e])
    return Le[e];
  var t = ti[e];
  if (t)
    for (var n = Object.keys(t), o = n.length, r = 0; r < o; r += 1) {
      var i = n[r];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in Ar)
        return Le[e] = t[i], Le[e];
    }
  return "";
}
var $r = Ir("animationend"), jr = Ir("transitionend"), zr = !!($r && jr), lr = $r || "animationend", ur = jr || "transitionend";
function fr(e, t) {
  if (!e) return null;
  if (k(e) === "object") {
    var n = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const ni = function(e) {
  var t = ee();
  function n(r) {
    r && (r.removeEventListener(ur, e), r.removeEventListener(lr, e));
  }
  function o(r) {
    t.current && t.current !== r && n(t.current), r && r !== t.current && (r.addEventListener(ur, e), r.addEventListener(lr, e), t.current = r);
  }
  return P.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [o, n];
};
var Dr = Ne() ? Qr : pe, kr = function(t) {
  return +setTimeout(t, 16);
}, Fr = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (kr = function(t) {
  return window.requestAnimationFrame(t);
}, Fr = function(t) {
  return window.cancelAnimationFrame(t);
});
var dr = 0, Rt = /* @__PURE__ */ new Map();
function Nr(e) {
  Rt.delete(e);
}
var St = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  dr += 1;
  var o = dr;
  function r(i) {
    if (i === 0)
      Nr(o), t();
    else {
      var s = kr(function() {
        r(i - 1);
      });
      Rt.set(o, s);
    }
  }
  return r(n), o;
};
St.cancel = function(e) {
  var t = Rt.get(e);
  return Nr(e), Fr(t);
};
const oi = function() {
  var e = P.useRef(null);
  function t() {
    St.cancel(e.current);
  }
  function n(o) {
    var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = St(function() {
      r <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : n(o, r - 1);
    });
    e.current = i;
  }
  return P.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var ii = [W, ce, le, Ot], si = [W, Lr], Hr = !1, ai = !0;
function Vr(e) {
  return e === le || e === Ot;
}
const ci = function(e, t, n) {
  var o = ve(ar), r = N(o, 2), i = r[0], s = r[1], a = oi(), c = N(a, 2), l = c[0], d = c[1];
  function u() {
    s(W, !0);
  }
  var f = t ? si : ii;
  return Dr(function() {
    if (i !== ar && i !== Ot) {
      var m = f.indexOf(i), v = f[m + 1], g = n(i);
      g === Hr ? s(v, !0) : v && l(function(h) {
        function S() {
          h.isCanceled() || s(v, !0);
        }
        g === !0 ? S() : Promise.resolve(g).then(S);
      });
    }
  }, [e, i]), P.useEffect(function() {
    return function() {
      d();
    };
  }, []), [u, i];
};
function li(e, t, n, o) {
  var r = o.motionEnter, i = r === void 0 ? !0 : r, s = o.motionAppear, a = s === void 0 ? !0 : s, c = o.motionLeave, l = c === void 0 ? !0 : c, d = o.motionDeadline, u = o.motionLeaveImmediately, f = o.onAppearPrepare, m = o.onEnterPrepare, v = o.onLeavePrepare, g = o.onAppearStart, h = o.onEnterStart, S = o.onLeaveStart, y = o.onAppearActive, _ = o.onEnterActive, b = o.onLeaveActive, w = o.onAppearEnd, p = o.onEnterEnd, M = o.onLeaveEnd, T = o.onVisibleChanged, R = ve(), L = N(R, 2), A = L[0], I = L[1], $ = Jo(J), j = N($, 2), z = j[0], V = j[1], te = ve(null), Z = N(te, 2), ye = Z[0], be = Z[1], B = z(), re = ee(!1), me = ee(null);
  function G() {
    return n();
  }
  var ne = ee(!1);
  function Se() {
    V(J), be(null, !0);
  }
  var Q = ge(function(H) {
    var F = z();
    if (F !== J) {
      var K = G();
      if (!(H && !H.deadline && H.target !== K)) {
        var we = ne.current, Te;
        F === Pe && we ? Te = w == null ? void 0 : w(K, H) : F === Oe && we ? Te = p == null ? void 0 : p(K, H) : F === Re && we && (Te = M == null ? void 0 : M(K, H)), we && Te !== !1 && Se();
      }
    }
  }), Ye = ni(Q), xe = N(Ye, 1), Ce = xe[0], Ee = function(F) {
    switch (F) {
      case Pe:
        return E(E(E({}, W, f), ce, g), le, y);
      case Oe:
        return E(E(E({}, W, m), ce, h), le, _);
      case Re:
        return E(E(E({}, W, v), ce, S), le, b);
      default:
        return {};
    }
  }, oe = P.useMemo(function() {
    return Ee(B);
  }, [B]), _e = ci(B, !e, function(H) {
    if (H === W) {
      var F = oe[W];
      return F ? F(G()) : Hr;
    }
    if (ie in oe) {
      var K;
      be(((K = oe[ie]) === null || K === void 0 ? void 0 : K.call(oe, G(), null)) || null);
    }
    return ie === le && B !== J && (Ce(G()), d > 0 && (clearTimeout(me.current), me.current = setTimeout(function() {
      Q({
        deadline: !0
      });
    }, d))), ie === Lr && Se(), ai;
  }), Lt = N(_e, 2), Ur = Lt[0], ie = Lt[1], Wr = Vr(ie);
  ne.current = Wr;
  var At = ee(null);
  Dr(function() {
    if (!(re.current && At.current === t)) {
      I(t);
      var H = re.current;
      re.current = !0;
      var F;
      !H && t && a && (F = Pe), H && t && i && (F = Oe), (H && !t && l || !H && u && !t && l) && (F = Re);
      var K = Ee(F);
      F && (e || K[W]) ? (V(F), Ur()) : V(J), At.current = t;
    }
  }, [t]), pe(function() {
    // Cancel appear
    (B === Pe && !a || // Cancel enter
    B === Oe && !i || // Cancel leave
    B === Re && !l) && V(J);
  }, [a, i, l]), pe(function() {
    return function() {
      re.current = !1, clearTimeout(me.current);
    };
  }, []);
  var Ze = P.useRef(!1);
  pe(function() {
    A && (Ze.current = !0), A !== void 0 && B === J && ((Ze.current || A) && (T == null || T(A)), Ze.current = !0);
  }, [A, B]);
  var Je = ye;
  return oe[W] && ie === ce && (Je = C({
    transition: "none"
  }, Je)), [B, ie, Je, A ?? t];
}
function ui(e) {
  var t = e;
  k(e) === "object" && (t = e.transitionSupport);
  function n(r, i) {
    return !!(r.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ P.forwardRef(function(r, i) {
    var s = r.visible, a = s === void 0 ? !0 : s, c = r.removeOnLeave, l = c === void 0 ? !0 : c, d = r.forceRender, u = r.children, f = r.motionName, m = r.leavedClassName, v = r.eventProps, g = P.useContext(Yo), h = g.motion, S = n(r, h), y = ee(), _ = ee();
    function b() {
      try {
        return y.current instanceof HTMLElement ? y.current : qo(_.current);
      } catch {
        return null;
      }
    }
    var w = li(S, a, b, r), p = N(w, 4), M = p[0], T = p[1], R = p[2], L = p[3], A = P.useRef(L);
    L && (A.current = !0);
    var I = P.useCallback(function(Z) {
      y.current = Z, Mo(i, Z);
    }, [i]), $, j = C(C({}, v), {}, {
      visible: a
    });
    if (!u)
      $ = null;
    else if (M === J)
      L ? $ = u(C({}, j), I) : !l && A.current && m ? $ = u(C(C({}, j), {}, {
        className: m
      }), I) : d || !l && !m ? $ = u(C(C({}, j), {}, {
        style: {
          display: "none"
        }
      }), I) : $ = null;
    else {
      var z;
      T === W ? z = "prepare" : Vr(T) ? z = "active" : T === ce && (z = "start");
      var V = fr(f, "".concat(M, "-").concat(z));
      $ = u(C(C({}, j), {}, {
        className: X(fr(f, M), E(E({}, V, V && z), f, typeof f == "string")),
        style: R
      }), I);
    }
    if (/* @__PURE__ */ P.isValidElement($) && Po($)) {
      var te = Oo($);
      te || ($ = /* @__PURE__ */ P.cloneElement($, {
        ref: I
      }));
    }
    return /* @__PURE__ */ P.createElement(Zo, {
      ref: _
    }, $);
  });
  return o.displayName = "CSSMotion", o;
}
const Br = ui(zr);
var xt = "add", Ct = "keep", Et = "remove", ct = "removed";
function fi(e) {
  var t;
  return e && k(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, C(C({}, t), {}, {
    key: String(t.key)
  });
}
function _t() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(fi);
}
function di() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], o = 0, r = t.length, i = _t(e), s = _t(t);
  i.forEach(function(l) {
    for (var d = !1, u = o; u < r; u += 1) {
      var f = s[u];
      if (f.key === l.key) {
        o < u && (n = n.concat(s.slice(o, u).map(function(m) {
          return C(C({}, m), {}, {
            status: xt
          });
        })), o = u), n.push(C(C({}, f), {}, {
          status: Ct
        })), o += 1, d = !0;
        break;
      }
    }
    d || n.push(C(C({}, l), {}, {
      status: Et
    }));
  }), o < r && (n = n.concat(s.slice(o).map(function(l) {
    return C(C({}, l), {}, {
      status: xt
    });
  })));
  var a = {};
  n.forEach(function(l) {
    var d = l.key;
    a[d] = (a[d] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(l) {
    return a[l] > 1;
  });
  return c.forEach(function(l) {
    n = n.filter(function(d) {
      var u = d.key, f = d.status;
      return u !== l || f !== Et;
    }), n.forEach(function(d) {
      d.key === l && (d.status = Ct);
    });
  }), n;
}
var mi = ["component", "children", "onVisibleChanged", "onAllRemoved"], hi = ["status"], pi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function gi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Br, n = /* @__PURE__ */ function(o) {
    ke(i, o);
    var r = Fe(i);
    function i() {
      var s;
      fe(this, i);
      for (var a = arguments.length, c = new Array(a), l = 0; l < a; l++)
        c[l] = arguments[l];
      return s = r.call.apply(r, [this].concat(c)), E(se(s), "state", {
        keyEntities: []
      }), E(se(s), "removeKey", function(d) {
        s.setState(function(u) {
          var f = u.keyEntities.map(function(m) {
            return m.key !== d ? m : C(C({}, m), {}, {
              status: ct
            });
          });
          return {
            keyEntities: f
          };
        }, function() {
          var u = s.state.keyEntities, f = u.filter(function(m) {
            var v = m.status;
            return v !== ct;
          }).length;
          f === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return de(i, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, l = this.props, d = l.component, u = l.children, f = l.onVisibleChanged;
        l.onAllRemoved;
        var m = sr(l, mi), v = d || P.Fragment, g = {};
        return pi.forEach(function(h) {
          g[h] = m[h], delete m[h];
        }), delete m.keys, /* @__PURE__ */ P.createElement(v, m, c.map(function(h, S) {
          var y = h.status, _ = sr(h, hi), b = y === xt || y === Ct;
          return /* @__PURE__ */ P.createElement(t, ue({}, g, {
            key: _.key,
            visible: b,
            eventProps: _,
            onVisibleChanged: function(p) {
              f == null || f(p, {
                key: _.key
              }), p || a.removeKey(_.key);
            }
          }), function(w, p) {
            return u(C(C({}, w), {}, {
              index: S
            }), p);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var l = a.keys, d = c.keyEntities, u = _t(l), f = di(d, u);
        return {
          keyEntities: f.filter(function(m) {
            var v = d.find(function(g) {
              var h = g.key;
              return m.key === h;
            });
            return !(v && v.status === ct && m.status === Et);
          })
        };
      }
    }]), i;
  }(P.Component);
  return E(n, "defaultProps", {
    component: "div"
  }), n;
}
gi(zr);
const lt = () => ({
  height: 0,
  opacity: 0
}), mr = (e) => {
  const {
    scrollHeight: t
  } = e;
  return {
    height: t,
    opacity: 1
  };
}, vi = (e) => ({
  height: e ? e.offsetHeight : 0
}), ut = (e, t) => (t == null ? void 0 : t.deadline) === !0 || t.propertyName === "height", yi = (e = ao) => ({
  motionName: `${e}-motion-collapse`,
  onAppearStart: lt,
  onEnterStart: lt,
  onAppearActive: mr,
  onEnterActive: mr,
  onLeaveStart: vi,
  onLeaveActive: lt,
  onAppearEnd: ut,
  onEnterEnd: ut,
  onLeaveEnd: ut,
  motionDeadline: 500
}), bi = (e, t, n) => {
  const o = typeof e == "boolean" || (e == null ? void 0 : e.expandedKeys) === void 0, [r, i, s] = x.useMemo(() => {
    let u = {
      expandedKeys: [],
      onExpand: () => {
      }
    };
    return e ? (typeof e == "object" && (u = {
      ...u,
      ...e
    }), [!0, u.expandedKeys, u.onExpand]) : [!1, u.expandedKeys, u.onExpand];
  }, [e]), [a, c] = bo(i, {
    value: o ? void 0 : i,
    onChange: s
  }), l = (u) => {
    c((f) => {
      const m = o ? f : i, v = m.includes(u) ? m.filter((g) => g !== u) : [...m, u];
      return s == null || s(v), v;
    });
  }, d = x.useMemo(() => r ? {
    ...yi(n),
    motionAppear: !1,
    leavedClassName: `${t}-content-hidden`
  } : {}, [n, t, r]);
  return [r, a, r ? l : void 0, d];
}, Si = (e) => ({
  [e.componentCls]: {
    // For common/openAnimation
    [`${e.antCls}-motion-collapse-legacy`]: {
      overflow: "hidden",
      "&-active": {
        transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
      }
    },
    [`${e.antCls}-motion-collapse`]: {
      overflow: "hidden",
      transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
    }
  }
});
let ft = /* @__PURE__ */ function(e) {
  return e.PENDING = "pending", e.SUCCESS = "success", e.ERROR = "error", e;
}({});
const Gr = /* @__PURE__ */ x.createContext(null), xi = (e) => {
  const {
    info: t = {},
    nextStatus: n,
    onClick: o,
    ...r
  } = e, i = Cr(r, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    prefixCls: s,
    collapseMotion: a,
    enableCollapse: c,
    expandedKeys: l,
    direction: d,
    classNames: u = {},
    styles: f = {}
  } = x.useContext(Gr), m = x.useId(), {
    key: v = m,
    icon: g,
    title: h,
    extra: S,
    content: y,
    footer: _,
    status: b,
    description: w
  } = t, p = `${s}-item`, M = () => o == null ? void 0 : o(v), T = l == null ? void 0 : l.includes(v);
  return /* @__PURE__ */ x.createElement("div", ue({}, i, {
    className: X(p, {
      [`${p}-${b}${n ? `-${n}` : ""}`]: b
    }, e.className),
    style: e.style
  }), /* @__PURE__ */ x.createElement("div", {
    className: X(`${p}-header`, u.itemHeader),
    style: f.itemHeader,
    onClick: M
  }, /* @__PURE__ */ x.createElement(an, {
    icon: g,
    className: `${p}-icon`
  }), /* @__PURE__ */ x.createElement("div", {
    className: X(`${p}-header-box`, {
      [`${p}-collapsible`]: c && y
    })
  }, /* @__PURE__ */ x.createElement(jt.Text, {
    strong: !0,
    ellipsis: {
      tooltip: {
        placement: d === "rtl" ? "topRight" : "topLeft",
        title: h
      }
    },
    className: `${p}-title`
  }, c && y && (d === "rtl" ? /* @__PURE__ */ x.createElement(fn, {
    className: `${p}-collapse-icon`,
    rotate: T ? -90 : 0
  }) : /* @__PURE__ */ x.createElement(dn, {
    className: `${p}-collapse-icon`,
    rotate: T ? 90 : 0
  })), h), w && /* @__PURE__ */ x.createElement(jt.Text, {
    className: `${p}-desc`,
    ellipsis: {
      tooltip: {
        placement: d === "rtl" ? "topRight" : "topLeft",
        title: w
      }
    },
    type: "secondary"
  }, w)), S && /* @__PURE__ */ x.createElement("div", {
    className: `${p}-extra`
  }, S)), y && /* @__PURE__ */ x.createElement(Br, ue({}, a, {
    visible: c ? T : !0
  }), ({
    className: R,
    style: L
  }, A) => /* @__PURE__ */ x.createElement("div", {
    className: X(`${p}-content`, R),
    ref: A,
    style: L
  }, /* @__PURE__ */ x.createElement("div", {
    className: X(`${p}-content-box`, u.itemContent),
    style: f.itemContent
  }, y))), _ && /* @__PURE__ */ x.createElement("div", {
    className: X(`${p}-footer`, u.itemFooter),
    style: f.itemFooter
  }, _));
}, Ci = (e) => {
  const {
    componentCls: t
  } = e, n = `${t}-item`, o = {
    [ft.PENDING]: e.colorPrimaryText,
    [ft.SUCCESS]: e.colorSuccessText,
    [ft.ERROR]: e.colorErrorText
  }, r = Object.keys(o);
  return r.reduce((i, s) => {
    const a = o[s];
    return r.forEach((c) => {
      const l = `& ${n}-${s}-${c}`, d = s === c ? {} : {
        backgroundColor: "none !important",
        backgroundImage: `linear-gradient(${a}, ${o[c]})`
      };
      i[l] = {
        [`& ${n}-icon, & > *::before`]: {
          backgroundColor: `${a} !important`
        },
        "& > :last-child::before": d
      };
    }), i;
  }, {});
}, Ei = (e) => {
  const {
    calc: t,
    componentCls: n
  } = e, o = `${n}-item`, r = {
    content: '""',
    width: t(e.lineWidth).mul(2).equal(),
    display: "block",
    position: "absolute",
    insetInlineEnd: "none",
    backgroundColor: e.colorTextPlaceholder
  };
  return {
    "& > :last-child > :last-child": {
      "&::before": {
        display: "none !important"
      },
      [`&${o}-footer`]: {
        "&::before": {
          display: "block !important",
          bottom: 0
        }
      }
    },
    [`& > ${o}`]: {
      [`& ${o}-header, & ${o}-content, & ${o}-footer`]: {
        position: "relative",
        "&::before": {
          bottom: t(e.itemGap).mul(-1).equal()
        }
      },
      [`& ${o}-header, & ${o}-content`]: {
        marginInlineStart: t(e.itemSize).mul(-1).equal(),
        "&::before": {
          ...r,
          insetInlineStart: t(e.itemSize).div(2).sub(e.lineWidth).equal()
        }
      },
      [`& ${o}-header::before`]: {
        top: e.itemSize,
        bottom: t(e.itemGap).mul(-2).equal()
      },
      [`& ${o}-content::before`]: {
        top: "100%"
      },
      [`& ${o}-footer::before`]: {
        ...r,
        top: 0,
        insetInlineStart: t(e.itemSize).div(-2).sub(e.lineWidth).equal()
      }
    }
  };
}, _i = (e) => {
  const {
    componentCls: t
  } = e, n = `${t}-item`;
  return {
    [n]: {
      display: "flex",
      flexDirection: "column",
      [`& ${n}-collapsible`]: {
        cursor: "pointer"
      },
      [`& ${n}-header`]: {
        display: "flex",
        marginBottom: e.itemGap,
        gap: e.itemGap,
        alignItems: "flex-start",
        [`& ${n}-icon`]: {
          height: e.itemSize,
          width: e.itemSize,
          fontSize: e.itemFontSize
        },
        [`& ${n}-extra`]: {
          height: e.itemSize,
          maxHeight: e.itemSize
        },
        [`& ${n}-header-box`]: {
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          [`& ${n}-title`]: {
            height: e.itemSize,
            lineHeight: `${je(e.itemSize)}`,
            maxHeight: e.itemSize,
            fontSize: e.itemFontSize,
            [`& ${n}-collapse-icon`]: {
              marginInlineEnd: e.marginXS
            }
          },
          [`& ${n}-desc`]: {
            fontSize: e.itemFontSize
          }
        }
      },
      [`& ${n}-content`]: {
        [`& ${n}-content-hidden`]: {
          display: "none"
        },
        [`& ${n}-content-box`]: {
          padding: e.itemGap,
          display: "inline-block",
          maxWidth: `calc(100% - ${e.itemSize})`,
          borderRadius: e.borderRadiusLG,
          backgroundColor: e.colorBgContainer,
          border: `${je(e.lineWidth)} ${e.lineType} ${e.colorBorderSecondary}`
        }
      },
      [`& ${n}-footer`]: {
        marginTop: e.itemGap,
        display: "inline-flex"
      }
    }
  };
}, dt = (e, t = "middle") => {
  const {
    componentCls: n
  } = e, o = {
    large: {
      itemSize: e.itemSizeLG,
      itemGap: e.itemGapLG,
      itemFontSize: e.itemFontSizeLG
    },
    middle: {
      itemSize: e.itemSize,
      itemGap: e.itemGap,
      itemFontSize: e.itemFontSize
    },
    small: {
      itemSize: e.itemSizeSM,
      itemGap: e.itemGapSM,
      itemFontSize: e.itemFontSizeSM
    }
  }[t];
  return {
    [`&${n}-${t}`]: {
      paddingInlineStart: o.itemSize,
      gap: o.itemGap,
      ..._i({
        ...e,
        ...o
      }),
      ...Ei({
        ...e,
        ...o
      })
    }
  };
}, wi = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      display: "flex",
      flexDirection: "column",
      ...Ci(e),
      ...dt(e),
      ...dt(e, "large"),
      ...dt(e, "small"),
      [`&${t}-rtl`]: {
        direction: "rtl"
      }
    }
  };
}, Ti = Wo("ThoughtChain", (e) => {
  const t = Pt(e, {
    // small size tokens
    itemFontSizeSM: e.fontSizeSM,
    itemSizeSM: e.calc(e.controlHeightXS).add(e.controlHeightSM).div(2).equal(),
    itemGapSM: e.marginSM,
    // default size tokens
    itemFontSize: e.fontSize,
    itemSize: e.calc(e.controlHeightSM).add(e.controlHeight).div(2).equal(),
    itemGap: e.margin,
    // large size tokens
    itemFontSizeLG: e.fontSizeLG,
    itemSizeLG: e.calc(e.controlHeight).add(e.controlHeightLG).div(2).equal(),
    itemGapLG: e.marginLG
  });
  return [wi(t), Si(t)];
}), Mi = (e) => {
  const {
    prefixCls: t,
    rootClassName: n,
    className: o,
    items: r,
    collapsible: i,
    styles: s = {},
    style: a,
    classNames: c = {},
    size: l = "middle",
    ...d
  } = e, u = Cr(d, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    getPrefixCls: f,
    direction: m
  } = vt(), v = f(), g = f("thought-chain", t), h = so("thoughtChain"), [S, y, _, b] = bi(i, g, v), [w, p, M] = Ti(g), T = X(o, n, g, h.className, p, M, {
    [`${g}-rtl`]: m === "rtl"
  }, `${g}-${l}`);
  return w(/* @__PURE__ */ x.createElement("div", ue({}, u, {
    className: T,
    style: {
      ...h.style,
      ...a
    }
  }), /* @__PURE__ */ x.createElement(Gr.Provider, {
    value: {
      prefixCls: g,
      enableCollapse: S,
      collapseMotion: b,
      expandedKeys: y,
      direction: m,
      classNames: {
        itemHeader: X(h.classNames.itemHeader, c.itemHeader),
        itemContent: X(h.classNames.itemContent, c.itemContent),
        itemFooter: X(h.classNames.itemFooter, c.itemFooter)
      },
      styles: {
        itemHeader: {
          ...h.styles.itemHeader,
          ...s.itemHeader
        },
        itemContent: {
          ...h.styles.itemContent,
          ...s.itemContent
        },
        itemFooter: {
          ...h.styles.itemFooter,
          ...s.itemFooter
        }
      }
    }
  }, r == null ? void 0 : r.map((R, L) => {
    var A;
    return /* @__PURE__ */ x.createElement(xi, {
      key: R.key || `key_${L}`,
      className: X(h.classNames.item, c.item),
      style: {
        ...h.styles.item,
        ...s.item
      },
      info: {
        ...R,
        icon: R.icon || L + 1
      },
      onClick: _,
      nextStatus: ((A = r[L + 1]) == null ? void 0 : A.status) || R.status
    });
  }))));
}, Pi = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Oi(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = Ri(n, o), t;
  }, {}) : {};
}
function Ri(e, t) {
  return typeof t == "number" && !Pi.includes(e) ? t + "px" : t;
}
function wt(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const r = x.Children.toArray(e._reactElement.props.children).map((i) => {
      if (x.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = wt(i.props.el);
        return x.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...x.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(mt(x.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: s,
      type: a,
      useCapture: c
    }) => {
      n.addEventListener(a, s, c);
    });
  });
  const o = Array.from(e.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = wt(i);
      t.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Li(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const hr = Yr(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = ee(), [a, c] = Zr([]), {
    forceClone: l
  } = nn(), d = l ? !0 : t;
  return pe(() => {
    var g;
    if (!s.current || !e)
      return;
    let u = e;
    function f() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), Li(i, h), n && h.classList.add(...n.split(" ")), o) {
        const S = Oi(o);
        Object.keys(S).forEach((y) => {
          h.style[y] = S[y];
        });
      }
    }
    let m = null, v = null;
    if (d && window.MutationObserver) {
      let h = function() {
        var b, w, p;
        (b = s.current) != null && b.contains(u) && ((w = s.current) == null || w.removeChild(u));
        const {
          portals: y,
          clonedElement: _
        } = wt(e);
        u = _, c(y), u.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          f();
        }, 50), (p = s.current) == null || p.appendChild(u);
      };
      h();
      const S = _n(() => {
        h(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      m = new window.MutationObserver(S), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", f(), (g = s.current) == null || g.appendChild(u);
    return () => {
      var h, S;
      u.style.display = "", (h = s.current) != null && h.contains(u) && ((S = s.current) == null || S.removeChild(u)), m == null || m.disconnect();
    };
  }, [e, d, n, o, i, r, l]), x.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Ai = ({
  children: e,
  ...t
}) => /* @__PURE__ */ q.jsx(q.Fragment, {
  children: e(t)
});
function Ii(e) {
  return x.createElement(Ai, {
    children: e
  });
}
function Xr(e, t, n) {
  const o = e.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, i) => {
      var l, d;
      if (typeof r != "object")
        return t != null && t.fallback ? t.fallback(r) : r;
      const s = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...r.props,
        key: ((l = r.props) == null ? void 0 : l.key) ?? (n ? `${n}-${i}` : `${i}`)
      }) : {
        ...r.props,
        key: ((d = r.props) == null ? void 0 : d.key) ?? (n ? `${n}-${i}` : `${i}`)
      };
      let a = s;
      Object.keys(r.slots).forEach((u) => {
        if (!r.slots[u] || !(r.slots[u] instanceof Element) && !r.slots[u].el)
          return;
        const f = u.split(".");
        f.forEach((y, _) => {
          a[y] || (a[y] = {}), _ !== f.length - 1 && (a = s[y]);
        });
        const m = r.slots[u];
        let v, g, h = (t == null ? void 0 : t.clone) ?? !1, S = t == null ? void 0 : t.forceClone;
        m instanceof Element ? v = m : (v = m.el, g = m.callback, h = m.clone ?? h, S = m.forceClone ?? S), S = S ?? !!g, a[f[f.length - 1]] = v ? g ? (...y) => (g(f[f.length - 1], y), /* @__PURE__ */ q.jsx($t, {
          ...r.ctx,
          params: y,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(hr, {
            slot: v,
            clone: h
          })
        })) : Ii((y) => /* @__PURE__ */ q.jsx($t, {
          ...r.ctx,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(hr, {
            ...y,
            slot: v,
            clone: h
          })
        })) : a[f[f.length - 1]], a = s;
      });
      const c = (t == null ? void 0 : t.children) || "children";
      return r[c] ? s[c] = Xr(r[c], t, `${i}`) : t != null && t.children && (s[c] = void 0, Reflect.deleteProperty(s, c)), s;
    });
}
const {
  useItems: $i,
  withItemsContextProvider: ji,
  ItemHandler: ki
} = on("antdx-thought-chain-items"), Fi = Qn(ji(["default", "items"], ({
  children: e,
  items: t,
  ...n
}) => {
  const {
    items: o
  } = $i(), r = o.items.length > 0 ? o.items : o.default;
  return /* @__PURE__ */ q.jsxs(q.Fragment, {
    children: [/* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ q.jsx(Mi, {
      ...n,
      items: Jr(() => t || Xr(r, {
        clone: !0
      }), [t, r])
    })]
  });
}));
export {
  Fi as ThoughtChain,
  Fi as default
};
