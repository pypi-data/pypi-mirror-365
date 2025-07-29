var Nn = (e) => {
  throw TypeError(e);
};
var Fn = (e, t, n) => t.has(e) || Nn("Cannot " + n);
var De = (e, t, n) => (Fn(e, t, "read from private field"), n ? n.call(e) : t.get(e)), On = (e, t, n) => t.has(e) ? Nn("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, n), jn = (e, t, n, r) => (Fn(e, t, "write to private field"), r ? r.call(e, n) : t.set(e, n), n);
import { i as Fo, a as ve, r as Oo, b as jo, Z as ft, g as ko, c as N, d as bn, e as mt, o as An } from "./Index-BOJ3xWQW.js";
const P = window.ms_globals.React, c = window.ms_globals.React, Io = window.ms_globals.React.isValidElement, Po = window.ms_globals.React.version, J = window.ms_globals.React.useRef, Mo = window.ms_globals.React.useLayoutEffect, Ee = window.ms_globals.React.useEffect, Lo = window.ms_globals.React.useCallback, fe = window.ms_globals.React.useMemo, No = window.ms_globals.React.forwardRef, Ze = window.ms_globals.React.useState, kn = window.ms_globals.ReactDOM, ht = window.ms_globals.ReactDOM.createPortal, Ao = window.ms_globals.antdIcons.FileTextFilled, zo = window.ms_globals.antdIcons.CloseCircleFilled, Do = window.ms_globals.antdIcons.FileExcelFilled, Ho = window.ms_globals.antdIcons.FileImageFilled, Bo = window.ms_globals.antdIcons.FileMarkdownFilled, Wo = window.ms_globals.antdIcons.FilePdfFilled, Vo = window.ms_globals.antdIcons.FilePptFilled, Xo = window.ms_globals.antdIcons.FileWordFilled, Uo = window.ms_globals.antdIcons.FileZipFilled, Go = window.ms_globals.antdIcons.PlusOutlined, qo = window.ms_globals.antdIcons.LeftOutlined, Ko = window.ms_globals.antdIcons.RightOutlined, Yo = window.ms_globals.antdIcons.CloseOutlined, Lr = window.ms_globals.antdIcons.CheckOutlined, Zo = window.ms_globals.antdIcons.DeleteOutlined, Qo = window.ms_globals.antdIcons.EditOutlined, Jo = window.ms_globals.antdIcons.SyncOutlined, es = window.ms_globals.antdIcons.DislikeOutlined, ts = window.ms_globals.antdIcons.LikeOutlined, ns = window.ms_globals.antdIcons.CopyOutlined, rs = window.ms_globals.antdIcons.EyeOutlined, os = window.ms_globals.antdIcons.ArrowDownOutlined, ss = window.ms_globals.antd.ConfigProvider, Qe = window.ms_globals.antd.theme, Nr = window.ms_globals.antd.Upload, is = window.ms_globals.antd.Progress, as = window.ms_globals.antd.Image, ie = window.ms_globals.antd.Button, Ce = window.ms_globals.antd.Flex, $e = window.ms_globals.antd.Typography, ls = window.ms_globals.antd.Avatar, cs = window.ms_globals.antd.Popconfirm, us = window.ms_globals.antd.Tooltip, ds = window.ms_globals.antd.Collapse, fs = window.ms_globals.antd.Input, Fr = window.ms_globals.createItemsContext.createItemsContext, ms = window.ms_globals.internalContext.useContextPropsContext, zn = window.ms_globals.internalContext.ContextPropsProvider, Ve = window.ms_globals.antdCssinjs.unit, Wt = window.ms_globals.antdCssinjs.token2CSSVar, Dn = window.ms_globals.antdCssinjs.useStyleRegister, ps = window.ms_globals.antdCssinjs.useCSSVarRegister, gs = window.ms_globals.antdCssinjs.createTheme, hs = window.ms_globals.antdCssinjs.useCacheToken, Or = window.ms_globals.antdCssinjs.Keyframes, vt = window.ms_globals.components.Markdown;
var vs = /\s/;
function ys(e) {
  for (var t = e.length; t-- && vs.test(e.charAt(t)); )
    ;
  return t;
}
var bs = /^\s+/;
function xs(e) {
  return e && e.slice(0, ys(e) + 1).replace(bs, "");
}
var Hn = NaN, Ss = /^[-+]0x[0-9a-f]+$/i, ws = /^0b[01]+$/i, _s = /^0o[0-7]+$/i, Es = parseInt;
function Bn(e) {
  if (typeof e == "number")
    return e;
  if (Fo(e))
    return Hn;
  if (ve(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = ve(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = xs(e);
  var n = ws.test(e);
  return n || _s.test(e) ? Es(e.slice(2), n ? 2 : 8) : Ss.test(e) ? Hn : +e;
}
var Vt = function() {
  return Oo.Date.now();
}, Cs = "Expected a function", Ts = Math.max, $s = Math.min;
function Rs(e, t, n) {
  var r, o, s, i, a, l, u = 0, m = !1, f = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(Cs);
  t = Bn(t) || 0, ve(n) && (m = !!n.leading, f = "maxWait" in n, s = f ? Ts(Bn(n.maxWait) || 0, t) : s, d = "trailing" in n ? !!n.trailing : d);
  function p(x) {
    var I = r, M = o;
    return r = o = void 0, u = x, i = e.apply(M, I), i;
  }
  function v(x) {
    return u = x, a = setTimeout(y, t), m ? p(x) : i;
  }
  function h(x) {
    var I = x - l, M = x - u, k = t - I;
    return f ? $s(k, s - M) : k;
  }
  function g(x) {
    var I = x - l, M = x - u;
    return l === void 0 || I >= t || I < 0 || f && M >= s;
  }
  function y() {
    var x = Vt();
    if (g(x))
      return _(x);
    a = setTimeout(y, h(x));
  }
  function _(x) {
    return a = void 0, d && r ? p(x) : (r = o = void 0, i);
  }
  function C() {
    a !== void 0 && clearTimeout(a), u = 0, r = l = o = a = void 0;
  }
  function T() {
    return a === void 0 ? i : _(Vt());
  }
  function $() {
    var x = Vt(), I = g(x);
    if (r = arguments, o = this, l = x, I) {
      if (a === void 0)
        return v(l);
      if (f)
        return clearTimeout(a), a = setTimeout(y, t), p(l);
    }
    return a === void 0 && (a = setTimeout(y, t)), i;
  }
  return $.cancel = C, $.flush = T, $;
}
function Is(e, t) {
  return jo(e, t);
}
var jr = {
  exports: {}
}, wt = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ps = c, Ms = Symbol.for("react.element"), Ls = Symbol.for("react.fragment"), Ns = Object.prototype.hasOwnProperty, Fs = Ps.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Os = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function kr(e, t, n) {
  var r, o = {}, s = null, i = null;
  n !== void 0 && (s = "" + n), t.key !== void 0 && (s = "" + t.key), t.ref !== void 0 && (i = t.ref);
  for (r in t) Ns.call(t, r) && !Os.hasOwnProperty(r) && (o[r] = t[r]);
  if (e && e.defaultProps) for (r in t = e.defaultProps, t) o[r] === void 0 && (o[r] = t[r]);
  return {
    $$typeof: Ms,
    type: e,
    key: s,
    ref: i,
    props: o,
    _owner: Fs.current
  };
}
wt.Fragment = Ls;
wt.jsx = kr;
wt.jsxs = kr;
jr.exports = wt;
var S = jr.exports;
const {
  SvelteComponent: js,
  assign: Wn,
  binding_callbacks: Vn,
  check_outros: ks,
  children: Ar,
  claim_element: zr,
  claim_space: As,
  component_subscribe: Xn,
  compute_slots: zs,
  create_slot: Ds,
  detach: He,
  element: Dr,
  empty: Un,
  exclude_internal_props: Gn,
  get_all_dirty_from_scope: Hs,
  get_slot_changes: Bs,
  group_outros: Ws,
  init: Vs,
  insert_hydration: pt,
  safe_not_equal: Xs,
  set_custom_element_data: Hr,
  space: Us,
  transition_in: gt,
  transition_out: tn,
  update_slot_base: Gs
} = window.__gradio__svelte__internal, {
  beforeUpdate: qs,
  getContext: Ks,
  onDestroy: Ys,
  setContext: Zs
} = window.__gradio__svelte__internal;
function qn(e) {
  let t, n;
  const r = (
    /*#slots*/
    e[7].default
  ), o = Ds(
    r,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Dr("svelte-slot"), o && o.c(), this.h();
    },
    l(s) {
      t = zr(s, "SVELTE-SLOT", {
        class: !0
      });
      var i = Ar(t);
      o && o.l(i), i.forEach(He), this.h();
    },
    h() {
      Hr(t, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      pt(s, t, i), o && o.m(t, null), e[9](t), n = !0;
    },
    p(s, i) {
      o && o.p && (!n || i & /*$$scope*/
      64) && Gs(
        o,
        r,
        s,
        /*$$scope*/
        s[6],
        n ? Bs(
          r,
          /*$$scope*/
          s[6],
          i,
          null
        ) : Hs(
          /*$$scope*/
          s[6]
        ),
        null
      );
    },
    i(s) {
      n || (gt(o, s), n = !0);
    },
    o(s) {
      tn(o, s), n = !1;
    },
    d(s) {
      s && He(t), o && o.d(s), e[9](null);
    }
  };
}
function Qs(e) {
  let t, n, r, o, s = (
    /*$$slots*/
    e[4].default && qn(e)
  );
  return {
    c() {
      t = Dr("react-portal-target"), n = Us(), s && s.c(), r = Un(), this.h();
    },
    l(i) {
      t = zr(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), Ar(t).forEach(He), n = As(i), s && s.l(i), r = Un(), this.h();
    },
    h() {
      Hr(t, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      pt(i, t, a), e[8](t), pt(i, n, a), s && s.m(i, a), pt(i, r, a), o = !0;
    },
    p(i, [a]) {
      /*$$slots*/
      i[4].default ? s ? (s.p(i, a), a & /*$$slots*/
      16 && gt(s, 1)) : (s = qn(i), s.c(), gt(s, 1), s.m(r.parentNode, r)) : s && (Ws(), tn(s, 1, 1, () => {
        s = null;
      }), ks());
    },
    i(i) {
      o || (gt(s), o = !0);
    },
    o(i) {
      tn(s), o = !1;
    },
    d(i) {
      i && (He(t), He(n), He(r)), e[8](null), s && s.d(i);
    }
  };
}
function Kn(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Js(e, t, n) {
  let r, o, {
    $$slots: s = {},
    $$scope: i
  } = t;
  const a = zs(s);
  let {
    svelteInit: l
  } = t;
  const u = ft(Kn(t)), m = ft();
  Xn(e, m, (T) => n(0, r = T));
  const f = ft();
  Xn(e, f, (T) => n(1, o = T));
  const d = [], p = Ks("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: h,
    subSlotIndex: g
  } = ko() || {}, y = l({
    parent: p,
    props: u,
    target: m,
    slot: f,
    slotKey: v,
    slotIndex: h,
    subSlotIndex: g,
    onDestroy(T) {
      d.push(T);
    }
  });
  Zs("$$ms-gr-react-wrapper", y), qs(() => {
    u.set(Kn(t));
  }), Ys(() => {
    d.forEach((T) => T());
  });
  function _(T) {
    Vn[T ? "unshift" : "push"](() => {
      r = T, m.set(r);
    });
  }
  function C(T) {
    Vn[T ? "unshift" : "push"](() => {
      o = T, f.set(o);
    });
  }
  return e.$$set = (T) => {
    n(17, t = Wn(Wn({}, t), Gn(T))), "svelteInit" in T && n(5, l = T.svelteInit), "$$scope" in T && n(6, i = T.$$scope);
  }, t = Gn(t), [r, o, m, f, a, l, i, s, _, C];
}
class ei extends js {
  constructor(t) {
    super(), Vs(this, t, Js, Qs, Xs, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: sc
} = window.__gradio__svelte__internal, Yn = window.ms_globals.rerender, Xt = window.ms_globals.tree;
function ti(e, t = {}) {
  function n(r) {
    const o = ft(), s = new ei({
      ...r,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: t.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, l = i.parent ?? Xt;
          return l.nodes = [...l.nodes, a], Yn({
            createPortal: ht,
            node: Xt
          }), i.onDestroy(() => {
            l.nodes = l.nodes.filter((u) => u.svelteInstance !== o), Yn({
              createPortal: ht,
              node: Xt
            });
          }), a;
        },
        ...r.props
      }
    });
    return o.set(s), s;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise.then(() => {
      r(n);
    });
  });
}
const ni = "1.5.0";
function ye() {
  return ye = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var r in n) ({}).hasOwnProperty.call(n, r) && (e[r] = n[r]);
    }
    return e;
  }, ye.apply(null, arguments);
}
function ee(e) {
  "@babel/helpers - typeof";
  return ee = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, ee(e);
}
function ri(e, t) {
  if (ee(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var r = n.call(e, t);
    if (ee(r) != "object") return r;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Br(e) {
  var t = ri(e, "string");
  return ee(t) == "symbol" ? t : t + "";
}
function A(e, t, n) {
  return (t = Br(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function Zn(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var r = Object.getOwnPropertySymbols(e);
    t && (r = r.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), n.push.apply(n, r);
  }
  return n;
}
function j(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Zn(Object(n), !0).forEach(function(r) {
      A(e, r, n[r]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Zn(Object(n)).forEach(function(r) {
      Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(n, r));
    });
  }
  return e;
}
var oi = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, si = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, ii = "".concat(oi, " ").concat(si).split(/[\s\n]+/), ai = "aria-", li = "data-";
function Qn(e, t) {
  return e.indexOf(t) === 0;
}
function ci(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  t === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? n = {
    aria: !0
  } : n = j({}, t);
  var r = {};
  return Object.keys(e).forEach(function(o) {
    // Aria
    (n.aria && (o === "role" || Qn(o, ai)) || // Data
    n.data && Qn(o, li) || // Attr
    n.attr && ii.includes(o)) && (r[o] = e[o]);
  }), r;
}
const ui = /* @__PURE__ */ c.createContext({}), di = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, _t = (e) => {
  const t = c.useContext(ui);
  return c.useMemo(() => ({
    ...di,
    ...t[e]
  }), [t[e]]);
};
function Re() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: r,
    theme: o
  } = c.useContext(ss.ConfigContext);
  return {
    theme: o,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: r
  };
}
function fi(e) {
  if (Array.isArray(e)) return e;
}
function mi(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var r, o, s, i, a = [], l = !0, u = !1;
    try {
      if (s = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (r = s.call(n)).done) && (a.push(r.value), a.length !== t); l = !0) ;
    } catch (m) {
      u = !0, o = m;
    } finally {
      try {
        if (!l && n.return != null && (i = n.return(), Object(i) !== i)) return;
      } finally {
        if (u) throw o;
      }
    }
    return a;
  }
}
function Jn(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
  return r;
}
function pi(e, t) {
  if (e) {
    if (typeof e == "string") return Jn(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? Jn(e, t) : void 0;
  }
}
function gi() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function te(e, t) {
  return fi(e) || mi(e, t) || pi(e, t) || gi();
}
function Ge(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function er(e, t) {
  for (var n = 0; n < t.length; n++) {
    var r = t[n];
    r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, Br(r.key), r);
  }
}
function qe(e, t, n) {
  return t && er(e.prototype, t), n && er(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function Le(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function nn(e, t) {
  return nn = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, r) {
    return n.__proto__ = r, n;
  }, nn(e, t);
}
function Et(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && nn(e, t);
}
function yt(e) {
  return yt = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, yt(e);
}
function Wr() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Wr = function() {
    return !!e;
  })();
}
function hi(e, t) {
  if (t && (ee(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Le(e);
}
function Ct(e) {
  var t = Wr();
  return function() {
    var n, r = yt(e);
    if (t) {
      var o = yt(this).constructor;
      n = Reflect.construct(r, arguments, o);
    } else n = r.apply(this, arguments);
    return hi(this, n);
  };
}
var Vr = /* @__PURE__ */ qe(function e() {
  Ge(this, e);
}), Xr = "CALC_UNIT", vi = new RegExp(Xr, "g");
function Ut(e) {
  return typeof e == "number" ? "".concat(e).concat(Xr) : e;
}
var yi = /* @__PURE__ */ function(e) {
  Et(n, e);
  var t = Ct(n);
  function n(r, o) {
    var s;
    Ge(this, n), s = t.call(this), A(Le(s), "result", ""), A(Le(s), "unitlessCssVar", void 0), A(Le(s), "lowPriority", void 0);
    var i = ee(r);
    return s.unitlessCssVar = o, r instanceof n ? s.result = "(".concat(r.result, ")") : i === "number" ? s.result = Ut(r) : i === "string" && (s.result = r), s;
  }
  return qe(n, [{
    key: "add",
    value: function(o) {
      return o instanceof n ? this.result = "".concat(this.result, " + ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " + ").concat(Ut(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof n ? this.result = "".concat(this.result, " - ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " - ").concat(Ut(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof n ? this.result = "".concat(this.result, " * ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " * ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof n ? this.result = "".concat(this.result, " / ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " / ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(o) {
      return this.lowPriority || o ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(o) {
      var s = this, i = o || {}, a = i.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(u) {
        return s.result.includes(u);
      }) && (l = !1), this.result = this.result.replace(vi, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Vr), bi = /* @__PURE__ */ function(e) {
  Et(n, e);
  var t = Ct(n);
  function n(r) {
    var o;
    return Ge(this, n), o = t.call(this), A(Le(o), "result", 0), r instanceof n ? o.result = r.result : typeof r == "number" && (o.result = r), o;
  }
  return qe(n, [{
    key: "add",
    value: function(o) {
      return o instanceof n ? this.result += o.result : typeof o == "number" && (this.result += o), this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof n ? this.result -= o.result : typeof o == "number" && (this.result -= o), this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return o instanceof n ? this.result *= o.result : typeof o == "number" && (this.result *= o), this;
    }
  }, {
    key: "div",
    value: function(o) {
      return o instanceof n ? this.result /= o.result : typeof o == "number" && (this.result /= o), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), n;
}(Vr), xi = function(t, n) {
  var r = t === "css" ? yi : bi;
  return function(o) {
    return new r(o, n);
  };
}, tr = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function Ne(e) {
  var t = P.useRef();
  t.current = e;
  var n = P.useCallback(function() {
    for (var r, o = arguments.length, s = new Array(o), i = 0; i < o; i++)
      s[i] = arguments[i];
    return (r = t.current) === null || r === void 0 ? void 0 : r.call.apply(r, [t].concat(s));
  }, []);
  return n;
}
function Tt() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var nr = Tt() ? P.useLayoutEffect : P.useEffect, Ur = function(t, n) {
  var r = P.useRef(!0);
  nr(function() {
    return t(r.current);
  }, n), nr(function() {
    return r.current = !1, function() {
      r.current = !0;
    };
  }, []);
}, rr = function(t, n) {
  Ur(function(r) {
    if (!r)
      return t();
  }, n);
};
function Je(e) {
  var t = P.useRef(!1), n = P.useState(e), r = te(n, 2), o = r[0], s = r[1];
  P.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function i(a, l) {
    l && t.current || s(a);
  }
  return [o, i];
}
function Gt(e) {
  return e !== void 0;
}
function Si(e, t) {
  var n = t || {}, r = n.defaultValue, o = n.value, s = n.onChange, i = n.postState, a = Je(function() {
    return Gt(o) ? o : Gt(r) ? typeof r == "function" ? r() : r : typeof e == "function" ? e() : e;
  }), l = te(a, 2), u = l[0], m = l[1], f = o !== void 0 ? o : u, d = i ? i(f) : f, p = Ne(s), v = Je([f]), h = te(v, 2), g = h[0], y = h[1];
  rr(function() {
    var C = g[0];
    u !== C && p(u, C);
  }, [g]), rr(function() {
    Gt(o) || m(o);
  }, [o]);
  var _ = Ne(function(C, T) {
    m(C, T), y([f], T);
  });
  return [d, _];
}
var Gr = {
  exports: {}
}, H = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var xn = Symbol.for("react.element"), Sn = Symbol.for("react.portal"), $t = Symbol.for("react.fragment"), Rt = Symbol.for("react.strict_mode"), It = Symbol.for("react.profiler"), Pt = Symbol.for("react.provider"), Mt = Symbol.for("react.context"), wi = Symbol.for("react.server_context"), Lt = Symbol.for("react.forward_ref"), Nt = Symbol.for("react.suspense"), Ft = Symbol.for("react.suspense_list"), Ot = Symbol.for("react.memo"), jt = Symbol.for("react.lazy"), _i = Symbol.for("react.offscreen"), qr;
qr = Symbol.for("react.module.reference");
function me(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case xn:
        switch (e = e.type, e) {
          case $t:
          case It:
          case Rt:
          case Nt:
          case Ft:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case wi:
              case Mt:
              case Lt:
              case jt:
              case Ot:
              case Pt:
                return e;
              default:
                return t;
            }
        }
      case Sn:
        return t;
    }
  }
}
H.ContextConsumer = Mt;
H.ContextProvider = Pt;
H.Element = xn;
H.ForwardRef = Lt;
H.Fragment = $t;
H.Lazy = jt;
H.Memo = Ot;
H.Portal = Sn;
H.Profiler = It;
H.StrictMode = Rt;
H.Suspense = Nt;
H.SuspenseList = Ft;
H.isAsyncMode = function() {
  return !1;
};
H.isConcurrentMode = function() {
  return !1;
};
H.isContextConsumer = function(e) {
  return me(e) === Mt;
};
H.isContextProvider = function(e) {
  return me(e) === Pt;
};
H.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === xn;
};
H.isForwardRef = function(e) {
  return me(e) === Lt;
};
H.isFragment = function(e) {
  return me(e) === $t;
};
H.isLazy = function(e) {
  return me(e) === jt;
};
H.isMemo = function(e) {
  return me(e) === Ot;
};
H.isPortal = function(e) {
  return me(e) === Sn;
};
H.isProfiler = function(e) {
  return me(e) === It;
};
H.isStrictMode = function(e) {
  return me(e) === Rt;
};
H.isSuspense = function(e) {
  return me(e) === Nt;
};
H.isSuspenseList = function(e) {
  return me(e) === Ft;
};
H.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === $t || e === It || e === Rt || e === Nt || e === Ft || e === _i || typeof e == "object" && e !== null && (e.$$typeof === jt || e.$$typeof === Ot || e.$$typeof === Pt || e.$$typeof === Mt || e.$$typeof === Lt || e.$$typeof === qr || e.getModuleId !== void 0);
};
H.typeOf = me;
Gr.exports = H;
var qt = Gr.exports, Ei = Symbol.for("react.element"), Ci = Symbol.for("react.transitional.element"), Ti = Symbol.for("react.fragment");
function $i(e) {
  return (
    // Base object type
    e && ee(e) === "object" && // React Element type
    (e.$$typeof === Ei || e.$$typeof === Ci) && // React Fragment type
    e.type === Ti
  );
}
var Ri = Number(Po.split(".")[0]), Ii = function(t, n) {
  typeof t == "function" ? t(n) : ee(t) === "object" && t && "current" in t && (t.current = n);
}, Pi = function(t) {
  var n, r;
  if (!t)
    return !1;
  if (Kr(t) && Ri >= 19)
    return !0;
  var o = qt.isMemo(t) ? t.type.type : t.type;
  return !(typeof o == "function" && !((n = o.prototype) !== null && n !== void 0 && n.render) && o.$$typeof !== qt.ForwardRef || typeof t == "function" && !((r = t.prototype) !== null && r !== void 0 && r.render) && t.$$typeof !== qt.ForwardRef);
};
function Kr(e) {
  return /* @__PURE__ */ Io(e) && !$i(e);
}
var Mi = function(t) {
  if (t && Kr(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function or(e, t, n, r) {
  var o = j({}, t[e]);
  if (r != null && r.deprecatedTokens) {
    var s = r.deprecatedTokens;
    s.forEach(function(a) {
      var l = te(a, 2), u = l[0], m = l[1];
      if (o != null && o[u] || o != null && o[m]) {
        var f;
        (f = o[m]) !== null && f !== void 0 || (o[m] = o == null ? void 0 : o[u]);
      }
    });
  }
  var i = j(j({}, n), o);
  return Object.keys(i).forEach(function(a) {
    i[a] === t[a] && delete i[a];
  }), i;
}
var Yr = typeof CSSINJS_STATISTIC < "u", rn = !0;
function Ke() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Yr)
    return Object.assign.apply(Object, [{}].concat(t));
  rn = !1;
  var r = {};
  return t.forEach(function(o) {
    if (ee(o) === "object") {
      var s = Object.keys(o);
      s.forEach(function(i) {
        Object.defineProperty(r, i, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return o[i];
          }
        });
      });
    }
  }), rn = !0, r;
}
var sr = {};
function Li() {
}
var Ni = function(t) {
  var n, r = t, o = Li;
  return Yr && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), r = new Proxy(t, {
    get: function(i, a) {
      if (rn) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return i[a];
    }
  }), o = function(i, a) {
    var l;
    sr[i] = {
      global: Array.from(n),
      component: j(j({}, (l = sr[i]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: r,
    keys: n,
    flush: o
  };
};
function ir(e, t, n) {
  if (typeof n == "function") {
    var r;
    return n(Ke(t, (r = t[e]) !== null && r !== void 0 ? r : {}));
  }
  return n ?? {};
}
function Fi(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, r = new Array(n), o = 0; o < n; o++)
        r[o] = arguments[o];
      return "max(".concat(r.map(function(s) {
        return Ve(s);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, r = new Array(n), o = 0; o < n; o++)
        r[o] = arguments[o];
      return "min(".concat(r.map(function(s) {
        return Ve(s);
      }).join(","), ")");
    }
  };
}
var Oi = 1e3 * 60 * 10, ji = /* @__PURE__ */ function() {
  function e() {
    Ge(this, e), A(this, "map", /* @__PURE__ */ new Map()), A(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), A(this, "nextID", 0), A(this, "lastAccessBeat", /* @__PURE__ */ new Map()), A(this, "accessBeat", 0);
  }
  return qe(e, [{
    key: "set",
    value: function(n, r) {
      this.clear();
      var o = this.getCompositeKey(n);
      this.map.set(o, r), this.lastAccessBeat.set(o, Date.now());
    }
  }, {
    key: "get",
    value: function(n) {
      var r = this.getCompositeKey(n), o = this.map.get(r);
      return this.lastAccessBeat.set(r, Date.now()), this.accessBeat += 1, o;
    }
  }, {
    key: "getCompositeKey",
    value: function(n) {
      var r = this, o = n.map(function(s) {
        return s && ee(s) === "object" ? "obj_".concat(r.getObjectID(s)) : "".concat(ee(s), "_").concat(s);
      });
      return o.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(n) {
      if (this.objectIDMap.has(n))
        return this.objectIDMap.get(n);
      var r = this.nextID;
      return this.objectIDMap.set(n, r), this.nextID += 1, r;
    }
  }, {
    key: "clear",
    value: function() {
      var n = this;
      if (this.accessBeat > 1e4) {
        var r = Date.now();
        this.lastAccessBeat.forEach(function(o, s) {
          r - o > Oi && (n.map.delete(s), n.lastAccessBeat.delete(s));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), ar = new ji();
function ki(e, t) {
  return c.useMemo(function() {
    var n = ar.get(t);
    if (n)
      return n;
    var r = e();
    return ar.set(t, r), r;
  }, t);
}
var Ai = function() {
  return {};
};
function zi(e) {
  var t = e.useCSP, n = t === void 0 ? Ai : t, r = e.useToken, o = e.usePrefix, s = e.getResetStyles, i = e.getCommonStyle, a = e.getCompUnitless;
  function l(d, p, v, h) {
    var g = Array.isArray(d) ? d[0] : d;
    function y(M) {
      return "".concat(String(g)).concat(M.slice(0, 1).toUpperCase()).concat(M.slice(1));
    }
    var _ = (h == null ? void 0 : h.unitless) || {}, C = typeof a == "function" ? a(d) : {}, T = j(j({}, C), {}, A({}, y("zIndexPopup"), !0));
    Object.keys(_).forEach(function(M) {
      T[y(M)] = _[M];
    });
    var $ = j(j({}, h), {}, {
      unitless: T,
      prefixToken: y
    }), x = m(d, p, v, $), I = u(g, v, $);
    return function(M) {
      var k = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : M, R = x(M, k), L = te(R, 2), F = L[1], b = I(k), w = te(b, 2), O = w[0], z = w[1];
      return [O, F, z];
    };
  }
  function u(d, p, v) {
    var h = v.unitless, g = v.injectStyle, y = g === void 0 ? !0 : g, _ = v.prefixToken, C = v.ignore, T = function(I) {
      var M = I.rootCls, k = I.cssVar, R = k === void 0 ? {} : k, L = r(), F = L.realToken;
      return ps({
        path: [d],
        prefix: R.prefix,
        key: R.key,
        unitless: h,
        ignore: C,
        token: F,
        scope: M
      }, function() {
        var b = ir(d, F, p), w = or(d, F, b, {
          deprecatedTokens: v == null ? void 0 : v.deprecatedTokens
        });
        return Object.keys(b).forEach(function(O) {
          w[_(O)] = w[O], delete w[O];
        }), w;
      }), null;
    }, $ = function(I) {
      var M = r(), k = M.cssVar;
      return [function(R) {
        return y && k ? /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(T, {
          rootCls: I,
          cssVar: k,
          component: d
        }), R) : R;
      }, k == null ? void 0 : k.key];
    };
    return $;
  }
  function m(d, p, v) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(d) ? d : [d, d], y = te(g, 1), _ = y[0], C = g.join("-"), T = e.layer || {
      name: "antd"
    };
    return function($) {
      var x = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : $, I = r(), M = I.theme, k = I.realToken, R = I.hashId, L = I.token, F = I.cssVar, b = o(), w = b.rootPrefixCls, O = b.iconPrefixCls, z = n(), D = F ? "css" : "js", W = ki(function() {
        var X = /* @__PURE__ */ new Set();
        return F && Object.keys(h.unitless || {}).forEach(function(K) {
          X.add(Wt(K, F.prefix)), X.add(Wt(K, tr(_, F.prefix)));
        }), xi(D, X);
      }, [D, _, F == null ? void 0 : F.prefix]), ne = Fi(D), se = ne.max, U = ne.min, B = {
        theme: M,
        token: L,
        hashId: R,
        nonce: function() {
          return z.nonce;
        },
        clientOnly: h.clientOnly,
        layer: T,
        // antd is always at top of styles
        order: h.order || -999
      };
      typeof s == "function" && Dn(j(j({}, B), {}, {
        clientOnly: !1,
        path: ["Shared", w]
      }), function() {
        return s(L, {
          prefix: {
            rootPrefixCls: w,
            iconPrefixCls: O
          },
          csp: z
        });
      });
      var G = Dn(j(j({}, B), {}, {
        path: [C, $, O]
      }), function() {
        if (h.injectStyle === !1)
          return [];
        var X = Ni(L), K = X.token, ae = X.flush, re = ir(_, k, v), Se = ".".concat($), je = or(_, k, re, {
          deprecatedTokens: h.deprecatedTokens
        });
        F && re && ee(re) === "object" && Object.keys(re).forEach(function(ze) {
          re[ze] = "var(".concat(Wt(ze, tr(_, F.prefix)), ")");
        });
        var ke = Ke(K, {
          componentCls: Se,
          prefixCls: $,
          iconCls: ".".concat(O),
          antCls: ".".concat(w),
          calc: W,
          // @ts-ignore
          max: se,
          // @ts-ignore
          min: U
        }, F ? re : je), Ae = p(ke, {
          hashId: R,
          prefixCls: $,
          rootPrefixCls: w,
          iconPrefixCls: O
        });
        ae(_, je);
        var we = typeof i == "function" ? i(ke, $, x, h.resetFont) : null;
        return [h.resetStyle === !1 ? null : we, Ae];
      });
      return [G, R];
    };
  }
  function f(d, p, v) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = m(d, p, v, j({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, h)), y = function(C) {
      var T = C.prefixCls, $ = C.rootCls, x = $ === void 0 ? T : $;
      return g(T, x), null;
    };
    return y;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: f,
    genComponentStyleHook: m
  };
}
const Di = {
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
}, Hi = Object.assign(Object.assign({}, Di), {
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
}), Z = Math.round;
function Kt(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], r = n.map((o) => parseFloat(o));
  for (let o = 0; o < 3; o += 1)
    r[o] = t(r[o] || 0, n[o] || "", o);
  return n[3] ? r[3] = n[3].includes("%") ? r[3] / 100 : r[3] : r[3] = 1, r;
}
const lr = (e, t, n) => n === 0 ? e : e / 100;
function Ye(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class xe {
  constructor(t) {
    A(this, "isValid", !0), A(this, "r", 0), A(this, "g", 0), A(this, "b", 0), A(this, "a", 1), A(this, "_h", void 0), A(this, "_s", void 0), A(this, "_l", void 0), A(this, "_v", void 0), A(this, "_max", void 0), A(this, "_min", void 0), A(this, "_brightness", void 0);
    function n(r) {
      return r[0] in t && r[1] in t && r[2] in t;
    }
    if (t) if (typeof t == "string") {
      let o = function(s) {
        return r.startsWith(s);
      };
      const r = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(r) ? this.fromHexString(r) : o("rgb") ? this.fromRgbString(r) : o("hsl") ? this.fromHslString(r) : (o("hsv") || o("hsb")) && this.fromHsvString(r);
    } else if (t instanceof xe)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = Ye(t.r), this.g = Ye(t.g), this.b = Ye(t.b), this.a = typeof t.a == "number" ? Ye(t.a, 1) : 1;
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
    function t(s) {
      const i = s / 255;
      return i <= 0.03928 ? i / 12.92 : Math.pow((i + 0.055) / 1.055, 2.4);
    }
    const n = t(this.r), r = t(this.g), o = t(this.b);
    return 0.2126 * n + 0.7152 * r + 0.0722 * o;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = Z(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const n = this.getHue(), r = this.getSaturation();
    let o = this.getLightness() - t / 100;
    return o < 0 && (o = 0), this._c({
      h: n,
      s: r,
      l: o,
      a: this.a
    });
  }
  lighten(t = 10) {
    const n = this.getHue(), r = this.getSaturation();
    let o = this.getLightness() + t / 100;
    return o > 1 && (o = 1), this._c({
      h: n,
      s: r,
      l: o,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, n = 50) {
    const r = this._c(t), o = n / 100, s = (a) => (r[a] - this[a]) * o + this[a], i = {
      r: Z(s("r")),
      g: Z(s("g")),
      b: Z(s("b")),
      a: Z(s("a") * 100) / 100
    };
    return this._c(i);
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
    const n = this._c(t), r = this.a + n.a * (1 - this.a), o = (s) => Z((this[s] * this.a + n[s] * n.a * (1 - this.a)) / r);
    return this._c({
      r: o("r"),
      g: o("g"),
      b: o("b"),
      a: r
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
    const r = (this.g || 0).toString(16);
    t += r.length === 2 ? r : "0" + r;
    const o = (this.b || 0).toString(16);
    if (t += o.length === 2 ? o : "0" + o, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const s = Z(this.a * 255).toString(16);
      t += s.length === 2 ? s : "0" + s;
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
    const t = this.getHue(), n = Z(this.getSaturation() * 100), r = Z(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${n}%,${r}%,${this.a})` : `hsl(${t},${n}%,${r}%)`;
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
  _sc(t, n, r) {
    const o = this.clone();
    return o[t] = Ye(n, r), o;
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
    function r(o, s) {
      return parseInt(n[o] + n[s || o], 16);
    }
    n.length < 6 ? (this.r = r(0), this.g = r(1), this.b = r(2), this.a = n[3] ? r(3) / 255 : 1) : (this.r = r(0, 1), this.g = r(2, 3), this.b = r(4, 5), this.a = n[6] ? r(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: n,
    l: r,
    a: o
  }) {
    if (this._h = t % 360, this._s = n, this._l = r, this.a = typeof o == "number" ? o : 1, n <= 0) {
      const d = Z(r * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let s = 0, i = 0, a = 0;
    const l = t / 60, u = (1 - Math.abs(2 * r - 1)) * n, m = u * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (s = u, i = m) : l >= 1 && l < 2 ? (s = m, i = u) : l >= 2 && l < 3 ? (i = u, a = m) : l >= 3 && l < 4 ? (i = m, a = u) : l >= 4 && l < 5 ? (s = m, a = u) : l >= 5 && l < 6 && (s = u, a = m);
    const f = r - u / 2;
    this.r = Z((s + f) * 255), this.g = Z((i + f) * 255), this.b = Z((a + f) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: r,
    a: o
  }) {
    this._h = t % 360, this._s = n, this._v = r, this.a = typeof o == "number" ? o : 1;
    const s = Z(r * 255);
    if (this.r = s, this.g = s, this.b = s, n <= 0)
      return;
    const i = t / 60, a = Math.floor(i), l = i - a, u = Z(r * (1 - n) * 255), m = Z(r * (1 - n * l) * 255), f = Z(r * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = f, this.b = u;
        break;
      case 1:
        this.r = m, this.b = u;
        break;
      case 2:
        this.r = u, this.b = f;
        break;
      case 3:
        this.r = u, this.g = m;
        break;
      case 4:
        this.r = f, this.g = u;
        break;
      case 5:
      default:
        this.g = u, this.b = m;
        break;
    }
  }
  fromHsvString(t) {
    const n = Kt(t, lr);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = Kt(t, lr);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = Kt(t, (r, o) => (
      // Convert percentage to number. e.g. 50% -> 128
      o.includes("%") ? Z(r / 100 * 255) : r
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Yt(e) {
  return e >= 0 && e <= 255;
}
function st(e, t) {
  const {
    r: n,
    g: r,
    b: o,
    a: s
  } = new xe(e).toRgb();
  if (s < 1)
    return e;
  const {
    r: i,
    g: a,
    b: l
  } = new xe(t).toRgb();
  for (let u = 0.01; u <= 1; u += 0.01) {
    const m = Math.round((n - i * (1 - u)) / u), f = Math.round((r - a * (1 - u)) / u), d = Math.round((o - l * (1 - u)) / u);
    if (Yt(m) && Yt(f) && Yt(d))
      return new xe({
        r: m,
        g: f,
        b: d,
        a: Math.round(u * 100) / 100
      }).toRgbString();
  }
  return new xe({
    r: n,
    g: r,
    b: o,
    a: 1
  }).toRgbString();
}
var Bi = function(e, t) {
  var n = {};
  for (var r in e) Object.prototype.hasOwnProperty.call(e, r) && t.indexOf(r) < 0 && (n[r] = e[r]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var o = 0, r = Object.getOwnPropertySymbols(e); o < r.length; o++)
    t.indexOf(r[o]) < 0 && Object.prototype.propertyIsEnumerable.call(e, r[o]) && (n[r[o]] = e[r[o]]);
  return n;
};
function Wi(e) {
  const {
    override: t
  } = e, n = Bi(e, ["override"]), r = Object.assign({}, t);
  Object.keys(Hi).forEach((d) => {
    delete r[d];
  });
  const o = Object.assign(Object.assign({}, n), r), s = 480, i = 576, a = 768, l = 992, u = 1200, m = 1600;
  if (o.motion === !1) {
    const d = "0s";
    o.motionDurationFast = d, o.motionDurationMid = d, o.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, o), {
    // ============== Background ============== //
    colorFillContent: o.colorFillSecondary,
    colorFillContentHover: o.colorFill,
    colorFillAlter: o.colorFillQuaternary,
    colorBgContainerDisabled: o.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: o.colorBgContainer,
    colorSplit: st(o.colorBorderSecondary, o.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: o.colorTextQuaternary,
    colorTextDisabled: o.colorTextQuaternary,
    colorTextHeading: o.colorText,
    colorTextLabel: o.colorTextSecondary,
    colorTextDescription: o.colorTextTertiary,
    colorTextLightSolid: o.colorWhite,
    colorHighlight: o.colorError,
    colorBgTextHover: o.colorFillSecondary,
    colorBgTextActive: o.colorFill,
    colorIcon: o.colorTextTertiary,
    colorIconHover: o.colorText,
    colorErrorOutline: st(o.colorErrorBg, o.colorBgContainer),
    colorWarningOutline: st(o.colorWarningBg, o.colorBgContainer),
    // Font
    fontSizeIcon: o.fontSizeSM,
    // Line
    lineWidthFocus: o.lineWidth * 3,
    // Control
    lineWidth: o.lineWidth,
    controlOutlineWidth: o.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: o.controlHeight / 2,
    controlItemBgHover: o.colorFillTertiary,
    controlItemBgActive: o.colorPrimaryBg,
    controlItemBgActiveHover: o.colorPrimaryBgHover,
    controlItemBgActiveDisabled: o.colorFill,
    controlTmpOutline: o.colorFillQuaternary,
    controlOutline: st(o.colorPrimaryBg, o.colorBgContainer),
    lineType: o.lineType,
    borderRadius: o.borderRadius,
    borderRadiusXS: o.borderRadiusXS,
    borderRadiusSM: o.borderRadiusSM,
    borderRadiusLG: o.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: o.sizeXXS,
    paddingXS: o.sizeXS,
    paddingSM: o.sizeSM,
    padding: o.size,
    paddingMD: o.sizeMD,
    paddingLG: o.sizeLG,
    paddingXL: o.sizeXL,
    paddingContentHorizontalLG: o.sizeLG,
    paddingContentVerticalLG: o.sizeMS,
    paddingContentHorizontal: o.sizeMS,
    paddingContentVertical: o.sizeSM,
    paddingContentHorizontalSM: o.size,
    paddingContentVerticalSM: o.sizeXS,
    marginXXS: o.sizeXXS,
    marginXS: o.sizeXS,
    marginSM: o.sizeSM,
    margin: o.size,
    marginMD: o.sizeMD,
    marginLG: o.sizeLG,
    marginXL: o.sizeXL,
    marginXXL: o.sizeXXL,
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
    screenXS: s,
    screenXSMin: s,
    screenXSMax: i - 1,
    screenSM: i,
    screenSMMin: i,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: l - 1,
    screenLG: l,
    screenLGMin: l,
    screenLGMax: u - 1,
    screenXL: u,
    screenXLMin: u,
    screenXLMax: m - 1,
    screenXXL: m,
    screenXXLMin: m,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new xe("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new xe("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new xe("rgba(0, 0, 0, 0.09)").toRgbString()}
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
  }), r);
}
const Vi = {
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
}, Xi = {
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
}, Ui = gs(Qe.defaultAlgorithm), Gi = {
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
}, Zr = (e, t, n) => {
  const r = n.getDerivativeToken(e), {
    override: o,
    ...s
  } = t;
  let i = {
    ...r,
    override: o
  };
  return i = Wi(i), s && Object.entries(s).forEach(([a, l]) => {
    const {
      theme: u,
      ...m
    } = l;
    let f = m;
    u && (f = Zr({
      ...i,
      ...m
    }, {
      override: m
    }, u)), i[a] = f;
  }), i;
};
function qi() {
  const {
    token: e,
    hashed: t,
    theme: n = Ui,
    override: r,
    cssVar: o
  } = c.useContext(Qe._internalContext), [s, i, a] = hs(n, [Qe.defaultSeed, e], {
    salt: `${ni}-${t || ""}`,
    override: r,
    getComputedToken: Zr,
    cssVar: o && {
      prefix: o.prefix,
      key: o.key,
      unitless: Vi,
      ignore: Xi,
      preserve: Gi
    }
  });
  return [n, a, t ? i : "", s, o];
}
const {
  genStyleHooks: kt
} = zi({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Re();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, r, o] = qi();
    return {
      theme: e,
      realToken: t,
      hashId: n,
      token: r,
      cssVar: o
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = Re();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), rt = /* @__PURE__ */ c.createContext(null);
function cr(e) {
  const {
    getDropContainer: t,
    className: n,
    prefixCls: r,
    children: o
  } = e, {
    disabled: s
  } = c.useContext(rt), [i, a] = c.useState(), [l, u] = c.useState(null);
  if (c.useEffect(() => {
    const d = t == null ? void 0 : t();
    i !== d && a(d);
  }, [t]), c.useEffect(() => {
    if (i) {
      const d = () => {
        u(!0);
      }, p = (g) => {
        g.preventDefault();
      }, v = (g) => {
        g.relatedTarget || u(!1);
      }, h = (g) => {
        u(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", d), document.addEventListener("dragover", p), document.addEventListener("dragleave", v), document.addEventListener("drop", h), () => {
        document.removeEventListener("dragenter", d), document.removeEventListener("dragover", p), document.removeEventListener("dragleave", v), document.removeEventListener("drop", h);
      };
    }
  }, [!!i]), !(t && i && !s))
    return null;
  const f = `${r}-drop-area`;
  return /* @__PURE__ */ ht(/* @__PURE__ */ c.createElement("div", {
    className: N(f, n, {
      [`${f}-on-body`]: i.tagName === "BODY"
    }),
    style: {
      display: l ? "block" : "none"
    }
  }, o), i);
}
function ur(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function Ki(e) {
  return e && ee(e) === "object" && ur(e.nativeElement) ? e.nativeElement : ur(e) ? e : null;
}
function Yi(e) {
  var t = Ki(e);
  if (t)
    return t;
  if (e instanceof c.Component) {
    var n;
    return (n = kn.findDOMNode) === null || n === void 0 ? void 0 : n.call(kn, e);
  }
  return null;
}
function Zi(e, t) {
  if (e == null) return {};
  var n = {};
  for (var r in e) if ({}.hasOwnProperty.call(e, r)) {
    if (t.indexOf(r) !== -1) continue;
    n[r] = e[r];
  }
  return n;
}
function dr(e, t) {
  if (e == null) return {};
  var n, r, o = Zi(e, t);
  if (Object.getOwnPropertySymbols) {
    var s = Object.getOwnPropertySymbols(e);
    for (r = 0; r < s.length; r++) n = s[r], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (o[n] = e[n]);
  }
  return o;
}
var Qi = /* @__PURE__ */ P.createContext({}), Ji = /* @__PURE__ */ function(e) {
  Et(n, e);
  var t = Ct(n);
  function n() {
    return Ge(this, n), t.apply(this, arguments);
  }
  return qe(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(P.Component);
function ea(e) {
  var t = P.useReducer(function(a) {
    return a + 1;
  }, 0), n = te(t, 2), r = n[1], o = P.useRef(e), s = Ne(function() {
    return o.current;
  }), i = Ne(function(a) {
    o.current = typeof a == "function" ? a(o.current) : a, r();
  });
  return [s, i];
}
var Te = "none", it = "appear", at = "enter", lt = "leave", fr = "none", ge = "prepare", Be = "start", We = "active", wn = "end", Qr = "prepared";
function mr(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function ta(e, t) {
  var n = {
    animationend: mr("Animation", "AnimationEnd"),
    transitionend: mr("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var na = ta(Tt(), typeof window < "u" ? window : {}), Jr = {};
if (Tt()) {
  var ra = document.createElement("div");
  Jr = ra.style;
}
var ct = {};
function eo(e) {
  if (ct[e])
    return ct[e];
  var t = na[e];
  if (t)
    for (var n = Object.keys(t), r = n.length, o = 0; o < r; o += 1) {
      var s = n[o];
      if (Object.prototype.hasOwnProperty.call(t, s) && s in Jr)
        return ct[e] = t[s], ct[e];
    }
  return "";
}
var to = eo("animationend"), no = eo("transitionend"), ro = !!(to && no), pr = to || "animationend", gr = no || "transitionend";
function hr(e, t) {
  if (!e) return null;
  if (ee(e) === "object") {
    var n = t.replace(/-\w/g, function(r) {
      return r[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const oa = function(e) {
  var t = J();
  function n(o) {
    o && (o.removeEventListener(gr, e), o.removeEventListener(pr, e));
  }
  function r(o) {
    t.current && t.current !== o && n(t.current), o && o !== t.current && (o.addEventListener(gr, e), o.addEventListener(pr, e), t.current = o);
  }
  return P.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [r, n];
};
var oo = Tt() ? Mo : Ee, so = function(t) {
  return +setTimeout(t, 16);
}, io = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (so = function(t) {
  return window.requestAnimationFrame(t);
}, io = function(t) {
  return window.cancelAnimationFrame(t);
});
var vr = 0, _n = /* @__PURE__ */ new Map();
function ao(e) {
  _n.delete(e);
}
var on = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  vr += 1;
  var r = vr;
  function o(s) {
    if (s === 0)
      ao(r), t();
    else {
      var i = so(function() {
        o(s - 1);
      });
      _n.set(r, i);
    }
  }
  return o(n), r;
};
on.cancel = function(e) {
  var t = _n.get(e);
  return ao(e), io(t);
};
const sa = function() {
  var e = P.useRef(null);
  function t() {
    on.cancel(e.current);
  }
  function n(r) {
    var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var s = on(function() {
      o <= 1 ? r({
        isCanceled: function() {
          return s !== e.current;
        }
      }) : n(r, o - 1);
    });
    e.current = s;
  }
  return P.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var ia = [ge, Be, We, wn], aa = [ge, Qr], lo = !1, la = !0;
function co(e) {
  return e === We || e === wn;
}
const ca = function(e, t, n) {
  var r = Je(fr), o = te(r, 2), s = o[0], i = o[1], a = sa(), l = te(a, 2), u = l[0], m = l[1];
  function f() {
    i(ge, !0);
  }
  var d = t ? aa : ia;
  return oo(function() {
    if (s !== fr && s !== wn) {
      var p = d.indexOf(s), v = d[p + 1], h = n(s);
      h === lo ? i(v, !0) : v && u(function(g) {
        function y() {
          g.isCanceled() || i(v, !0);
        }
        h === !0 ? y() : Promise.resolve(h).then(y);
      });
    }
  }, [e, s]), P.useEffect(function() {
    return function() {
      m();
    };
  }, []), [f, s];
};
function ua(e, t, n, r) {
  var o = r.motionEnter, s = o === void 0 ? !0 : o, i = r.motionAppear, a = i === void 0 ? !0 : i, l = r.motionLeave, u = l === void 0 ? !0 : l, m = r.motionDeadline, f = r.motionLeaveImmediately, d = r.onAppearPrepare, p = r.onEnterPrepare, v = r.onLeavePrepare, h = r.onAppearStart, g = r.onEnterStart, y = r.onLeaveStart, _ = r.onAppearActive, C = r.onEnterActive, T = r.onLeaveActive, $ = r.onAppearEnd, x = r.onEnterEnd, I = r.onLeaveEnd, M = r.onVisibleChanged, k = Je(), R = te(k, 2), L = R[0], F = R[1], b = ea(Te), w = te(b, 2), O = w[0], z = w[1], D = Je(null), W = te(D, 2), ne = W[0], se = W[1], U = O(), B = J(!1), G = J(null);
  function X() {
    return n();
  }
  var K = J(!1);
  function ae() {
    z(Te), se(null, !0);
  }
  var re = Ne(function(Q) {
    var Y = O();
    if (Y !== Te) {
      var le = X();
      if (!(Q && !Q.deadline && Q.target !== le)) {
        var Ie = K.current, Pe;
        Y === it && Ie ? Pe = $ == null ? void 0 : $(le, Q) : Y === at && Ie ? Pe = x == null ? void 0 : x(le, Q) : Y === lt && Ie && (Pe = I == null ? void 0 : I(le, Q)), Ie && Pe !== !1 && ae();
      }
    }
  }), Se = oa(re), je = te(Se, 1), ke = je[0], Ae = function(Y) {
    switch (Y) {
      case it:
        return A(A(A({}, ge, d), Be, h), We, _);
      case at:
        return A(A(A({}, ge, p), Be, g), We, C);
      case lt:
        return A(A(A({}, ge, v), Be, y), We, T);
      default:
        return {};
    }
  }, we = P.useMemo(function() {
    return Ae(U);
  }, [U]), ze = ca(U, !e, function(Q) {
    if (Q === ge) {
      var Y = we[ge];
      return Y ? Y(X()) : lo;
    }
    if (E in we) {
      var le;
      se(((le = we[E]) === null || le === void 0 ? void 0 : le.call(we, X(), null)) || null);
    }
    return E === We && U !== Te && (ke(X()), m > 0 && (clearTimeout(G.current), G.current = setTimeout(function() {
      re({
        deadline: !0
      });
    }, m))), E === Qr && ae(), la;
  }), ot = te(ze, 2), Bt = ot[0], E = ot[1], q = co(E);
  K.current = q;
  var V = J(null);
  oo(function() {
    if (!(B.current && V.current === t)) {
      F(t);
      var Q = B.current;
      B.current = !0;
      var Y;
      !Q && t && a && (Y = it), Q && t && s && (Y = at), (Q && !t && u || !Q && f && !t && u) && (Y = lt);
      var le = Ae(Y);
      Y && (e || le[ge]) ? (z(Y), Bt()) : z(Te), V.current = t;
    }
  }, [t]), Ee(function() {
    // Cancel appear
    (U === it && !a || // Cancel enter
    U === at && !s || // Cancel leave
    U === lt && !u) && z(Te);
  }, [a, s, u]), Ee(function() {
    return function() {
      B.current = !1, clearTimeout(G.current);
    };
  }, []);
  var pe = P.useRef(!1);
  Ee(function() {
    L && (pe.current = !0), L !== void 0 && U === Te && ((pe.current || L) && (M == null || M(L)), pe.current = !0);
  }, [L, U]);
  var de = ne;
  return we[ge] && E === Be && (de = j({
    transition: "none"
  }, de)), [U, E, de, L ?? t];
}
function da(e) {
  var t = e;
  ee(e) === "object" && (t = e.transitionSupport);
  function n(o, s) {
    return !!(o.motionName && t && s !== !1);
  }
  var r = /* @__PURE__ */ P.forwardRef(function(o, s) {
    var i = o.visible, a = i === void 0 ? !0 : i, l = o.removeOnLeave, u = l === void 0 ? !0 : l, m = o.forceRender, f = o.children, d = o.motionName, p = o.leavedClassName, v = o.eventProps, h = P.useContext(Qi), g = h.motion, y = n(o, g), _ = J(), C = J();
    function T() {
      try {
        return _.current instanceof HTMLElement ? _.current : Yi(C.current);
      } catch {
        return null;
      }
    }
    var $ = ua(y, a, T, o), x = te($, 4), I = x[0], M = x[1], k = x[2], R = x[3], L = P.useRef(R);
    R && (L.current = !0);
    var F = P.useCallback(function(W) {
      _.current = W, Ii(s, W);
    }, [s]), b, w = j(j({}, v), {}, {
      visible: a
    });
    if (!f)
      b = null;
    else if (I === Te)
      R ? b = f(j({}, w), F) : !u && L.current && p ? b = f(j(j({}, w), {}, {
        className: p
      }), F) : m || !u && !p ? b = f(j(j({}, w), {}, {
        style: {
          display: "none"
        }
      }), F) : b = null;
    else {
      var O;
      M === ge ? O = "prepare" : co(M) ? O = "active" : M === Be && (O = "start");
      var z = hr(d, "".concat(I, "-").concat(O));
      b = f(j(j({}, w), {}, {
        className: N(hr(d, I), A(A({}, z, z && O), d, typeof d == "string")),
        style: k
      }), F);
    }
    if (/* @__PURE__ */ P.isValidElement(b) && Pi(b)) {
      var D = Mi(b);
      D || (b = /* @__PURE__ */ P.cloneElement(b, {
        ref: F
      }));
    }
    return /* @__PURE__ */ P.createElement(Ji, {
      ref: C
    }, b);
  });
  return r.displayName = "CSSMotion", r;
}
const fa = da(ro);
var sn = "add", an = "keep", ln = "remove", Zt = "removed";
function ma(e) {
  var t;
  return e && ee(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, j(j({}, t), {}, {
    key: String(t.key)
  });
}
function cn() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(ma);
}
function pa() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], r = 0, o = t.length, s = cn(e), i = cn(t);
  s.forEach(function(u) {
    for (var m = !1, f = r; f < o; f += 1) {
      var d = i[f];
      if (d.key === u.key) {
        r < f && (n = n.concat(i.slice(r, f).map(function(p) {
          return j(j({}, p), {}, {
            status: sn
          });
        })), r = f), n.push(j(j({}, d), {}, {
          status: an
        })), r += 1, m = !0;
        break;
      }
    }
    m || n.push(j(j({}, u), {}, {
      status: ln
    }));
  }), r < o && (n = n.concat(i.slice(r).map(function(u) {
    return j(j({}, u), {}, {
      status: sn
    });
  })));
  var a = {};
  n.forEach(function(u) {
    var m = u.key;
    a[m] = (a[m] || 0) + 1;
  });
  var l = Object.keys(a).filter(function(u) {
    return a[u] > 1;
  });
  return l.forEach(function(u) {
    n = n.filter(function(m) {
      var f = m.key, d = m.status;
      return f !== u || d !== ln;
    }), n.forEach(function(m) {
      m.key === u && (m.status = an);
    });
  }), n;
}
var ga = ["component", "children", "onVisibleChanged", "onAllRemoved"], ha = ["status"], va = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function ya(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : fa, n = /* @__PURE__ */ function(r) {
    Et(s, r);
    var o = Ct(s);
    function s() {
      var i;
      Ge(this, s);
      for (var a = arguments.length, l = new Array(a), u = 0; u < a; u++)
        l[u] = arguments[u];
      return i = o.call.apply(o, [this].concat(l)), A(Le(i), "state", {
        keyEntities: []
      }), A(Le(i), "removeKey", function(m) {
        i.setState(function(f) {
          var d = f.keyEntities.map(function(p) {
            return p.key !== m ? p : j(j({}, p), {}, {
              status: Zt
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var f = i.state.keyEntities, d = f.filter(function(p) {
            var v = p.status;
            return v !== Zt;
          }).length;
          d === 0 && i.props.onAllRemoved && i.props.onAllRemoved();
        });
      }), i;
    }
    return qe(s, [{
      key: "render",
      value: function() {
        var a = this, l = this.state.keyEntities, u = this.props, m = u.component, f = u.children, d = u.onVisibleChanged;
        u.onAllRemoved;
        var p = dr(u, ga), v = m || P.Fragment, h = {};
        return va.forEach(function(g) {
          h[g] = p[g], delete p[g];
        }), delete p.keys, /* @__PURE__ */ P.createElement(v, p, l.map(function(g, y) {
          var _ = g.status, C = dr(g, ha), T = _ === sn || _ === an;
          return /* @__PURE__ */ P.createElement(t, ye({}, h, {
            key: C.key,
            visible: T,
            eventProps: C,
            onVisibleChanged: function(x) {
              d == null || d(x, {
                key: C.key
              }), x || a.removeKey(C.key);
            }
          }), function($, x) {
            return f(j(j({}, $), {}, {
              index: y
            }), x);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, l) {
        var u = a.keys, m = l.keyEntities, f = cn(u), d = pa(m, f);
        return {
          keyEntities: d.filter(function(p) {
            var v = m.find(function(h) {
              var g = h.key;
              return p.key === g;
            });
            return !(v && v.status === Zt && p.status === ln);
          })
        };
      }
    }]), s;
  }(P.Component);
  return A(n, "defaultProps", {
    component: "div"
  }), n;
}
const ba = ya(ro);
function xa(e, t) {
  const {
    children: n,
    upload: r,
    rootClassName: o
  } = e, s = c.useRef(null);
  return c.useImperativeHandle(t, () => s.current), /* @__PURE__ */ c.createElement(Nr, ye({}, r, {
    showUploadList: !1,
    rootClassName: o,
    ref: s
  }), n);
}
const uo = /* @__PURE__ */ c.forwardRef(xa), Sa = (e) => {
  const {
    componentCls: t,
    antCls: n,
    calc: r
  } = e, o = `${t}-list-card`, s = r(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [o]: {
      borderRadius: e.borderRadius,
      position: "relative",
      background: e.colorFillContent,
      borderWidth: e.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${o}-name,${o}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${o}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${o}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: r(e.paddingSM).sub(e.lineWidth).equal(),
        paddingInlineStart: r(e.padding).add(e.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: e.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${o}-icon`]: {
          fontSize: r(e.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: r(e.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${o}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${o}-desc`]: {
          color: e.colorTextTertiary
        }
      },
      // ============================== Preview ==============================
      "&-type-preview": {
        width: s,
        height: s,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${o}-status-error)`]: {
          border: 0
        },
        // Img
        [`${n}-image`]: {
          width: "100%",
          height: "100%",
          borderRadius: "inherit",
          position: "relative",
          overflow: "hidden",
          img: {
            height: "100%",
            objectFit: "cover",
            borderRadius: "inherit"
          }
        },
        // Mask
        [`${o}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${e.opacityLoading})`
        },
        // Error
        [`&${o}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${o}-img-mask`]: {
            borderRadius: r(e.borderRadius).sub(e.lineWidth).equal()
          },
          [`${o}-desc`]: {
            paddingInline: e.paddingXXS
          }
        },
        // Progress
        [`${o}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${o}-remove`]: {
        position: "absolute",
        top: 0,
        insetInlineEnd: 0,
        border: 0,
        padding: e.paddingXXS,
        background: "transparent",
        lineHeight: 1,
        transform: "translate(50%, -50%)",
        fontSize: e.fontSize,
        cursor: "pointer",
        opacity: e.opacityLoading,
        display: "none",
        "&:dir(rtl)": {
          transform: "translate(-50%, -50%)"
        },
        "&:hover": {
          opacity: 1
        },
        "&:active": {
          opacity: e.opacityLoading
        }
      },
      [`&:hover ${o}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: e.colorError,
        [`${o}-desc`]: {
          color: e.colorError
        }
      },
      // ============================== Motion ===============================
      "&-motion": {
        transition: ["opacity", "width", "margin", "padding"].map((i) => `${i} ${e.motionDurationSlow}`).join(","),
        "&-appear-start": {
          width: 0,
          transition: "none"
        },
        "&-leave-active": {
          opacity: 0,
          width: 0,
          paddingInline: 0,
          borderInlineWidth: 0,
          marginInlineEnd: r(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, un = {
  "&, *": {
    boxSizing: "border-box"
  }
}, wa = (e) => {
  const {
    componentCls: t,
    calc: n,
    antCls: r
  } = e, o = `${t}-drop-area`, s = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [o]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...un,
      "&-on-body": {
        position: "fixed",
        inset: 0
      },
      "&-hide-placement": {
        [`${s}-inner`]: {
          display: "none"
        }
      },
      [s]: {
        padding: 0
      }
    },
    "&": {
      // ============================= Placeholder =============================
      [s]: {
        height: "100%",
        borderRadius: e.borderRadius,
        borderWidth: e.lineWidthBold,
        borderStyle: "dashed",
        borderColor: "transparent",
        padding: e.padding,
        position: "relative",
        backdropFilter: "blur(10px)",
        background: e.colorBgPlaceholderHover,
        ...un,
        [`${r}-upload-wrapper ${r}-upload${r}-upload-btn`]: {
          padding: 0
        },
        [`&${s}-drag-in`]: {
          borderColor: e.colorPrimaryHover
        },
        [`&${s}-disabled`]: {
          opacity: 0.25,
          pointerEvents: "none"
        },
        [`${s}-inner`]: {
          gap: n(e.paddingXXS).div(2).equal()
        },
        [`${s}-icon`]: {
          fontSize: e.fontSizeHeading2,
          lineHeight: 1
        },
        [`${s}-title${s}-title`]: {
          margin: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight
        },
        [`${s}-description`]: {}
      }
    }
  };
}, _a = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, r = `${t}-list`, o = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...un,
      // =============================== File List ===============================
      [r]: {
        display: "flex",
        flexWrap: "wrap",
        gap: e.paddingSM,
        fontSize: e.fontSize,
        lineHeight: e.lineHeight,
        color: e.colorText,
        paddingBlock: e.paddingSM,
        paddingInline: e.padding,
        width: "100%",
        background: e.colorBgContainer,
        // Hide scrollbar
        scrollbarWidth: "none",
        "-ms-overflow-style": "none",
        "&::-webkit-scrollbar": {
          display: "none"
        },
        // Scroll
        "&-overflow-scrollX, &-overflow-scrollY": {
          "&:before, &:after": {
            content: '""',
            position: "absolute",
            opacity: 0,
            transition: `opacity ${e.motionDurationSlow}`,
            zIndex: 1
          }
        },
        "&-overflow-ping-start:before": {
          opacity: 1
        },
        "&-overflow-ping-end:after": {
          opacity: 1
        },
        "&-overflow-scrollX": {
          overflowX: "auto",
          overflowY: "hidden",
          flexWrap: "nowrap",
          "&:before, &:after": {
            insetBlock: 0,
            width: 8
          },
          "&:before": {
            insetInlineStart: 0,
            background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetInlineEnd: 0,
            background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:dir(rtl)": {
            "&:before": {
              background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            },
            "&:after": {
              background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            }
          }
        },
        "&-overflow-scrollY": {
          overflowX: "hidden",
          overflowY: "auto",
          maxHeight: n(o).mul(3).equal(),
          "&:before, &:after": {
            insetInline: 0,
            height: 8
          },
          "&:before": {
            insetBlockStart: 0,
            background: "linear-gradient(to bottom, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetBlockEnd: 0,
            background: "linear-gradient(to top, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          }
        },
        // ======================================================================
        // ==                              Upload                              ==
        // ======================================================================
        "&-upload-btn": {
          width: o,
          height: o,
          fontSize: e.fontSizeHeading2,
          color: "#999"
        },
        // ======================================================================
        // ==                             PrevNext                             ==
        // ======================================================================
        "&-prev-btn, &-next-btn": {
          position: "absolute",
          top: "50%",
          transform: "translateY(-50%)",
          boxShadow: e.boxShadowTertiary,
          opacity: 0,
          pointerEvents: "none"
        },
        "&-prev-btn": {
          left: {
            _skip_check_: !0,
            value: e.padding
          }
        },
        "&-next-btn": {
          right: {
            _skip_check_: !0,
            value: e.padding
          }
        },
        "&:dir(ltr)": {
          [`&${r}-overflow-ping-start ${r}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${r}-overflow-ping-end ${r}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${r}-overflow-ping-end ${r}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${r}-overflow-ping-start ${r}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, Ea = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new xe(t).setA(0.85).toRgbString()
  };
}, fo = kt("Attachments", (e) => {
  const t = Ke(e, {});
  return [wa(t), _a(t), Sa(t)];
}, Ea), Ca = (e) => e.indexOf("image/") === 0, ut = 200;
function Ta(e) {
  return new Promise((t) => {
    if (!e || !e.type || !Ca(e.type)) {
      t("");
      return;
    }
    const n = new Image();
    if (n.onload = () => {
      const {
        width: r,
        height: o
      } = n, s = r / o, i = s > 1 ? ut : ut * s, a = s > 1 ? ut / s : ut, l = document.createElement("canvas");
      l.width = i, l.height = a, l.style.cssText = `position: fixed; left: 0; top: 0; width: ${i}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(l), l.getContext("2d").drawImage(n, 0, 0, i, a);
      const m = l.toDataURL();
      document.body.removeChild(l), window.URL.revokeObjectURL(n.src), t(m);
    }, n.crossOrigin = "anonymous", e.type.startsWith("image/svg+xml")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && typeof r.result == "string" && (n.src = r.result);
      }, r.readAsDataURL(e);
    } else if (e.type.startsWith("image/gif")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && t(r.result);
      }, r.readAsDataURL(e);
    } else
      n.src = window.URL.createObjectURL(e);
  });
}
function $a() {
  return /* @__PURE__ */ c.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ c.createElement("title", null, "audio"), /* @__PURE__ */ c.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ c.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function Ra(e) {
  const {
    percent: t
  } = e, {
    token: n
  } = Qe.useToken();
  return /* @__PURE__ */ c.createElement(is, {
    type: "circle",
    percent: t,
    size: n.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (r) => /* @__PURE__ */ c.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (r || 0).toFixed(0), "%")
  });
}
function Ia() {
  return /* @__PURE__ */ c.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ c.createElement("title", null, "video"), /* @__PURE__ */ c.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ c.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const Qt = " ", dn = "#8c8c8c", mo = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], Pa = [{
  icon: /* @__PURE__ */ c.createElement(Do, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  icon: /* @__PURE__ */ c.createElement(Ho, null),
  color: dn,
  ext: mo
}, {
  icon: /* @__PURE__ */ c.createElement(Bo, null),
  color: dn,
  ext: ["md", "mdx"]
}, {
  icon: /* @__PURE__ */ c.createElement(Wo, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  icon: /* @__PURE__ */ c.createElement(Vo, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  icon: /* @__PURE__ */ c.createElement(Xo, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  icon: /* @__PURE__ */ c.createElement(Uo, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  icon: /* @__PURE__ */ c.createElement(Ia, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  icon: /* @__PURE__ */ c.createElement($a, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function yr(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
function Ma(e) {
  let t = e;
  const n = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let r = 0;
  for (; t >= 1024 && r < n.length - 1; )
    t /= 1024, r++;
  return `${t.toFixed(0)} ${n[r]}`;
}
function La(e, t) {
  const {
    prefixCls: n,
    item: r,
    onRemove: o,
    className: s,
    style: i,
    imageProps: a
  } = e, l = c.useContext(rt), {
    disabled: u
  } = l || {}, {
    name: m,
    size: f,
    percent: d,
    status: p = "done",
    description: v
  } = r, {
    getPrefixCls: h
  } = Re(), g = h("attachment", n), y = `${g}-list-card`, [_, C, T] = fo(g), [$, x] = c.useMemo(() => {
    const z = m || "", D = z.match(/^(.*)\.[^.]+$/);
    return D ? [D[1], z.slice(D[1].length)] : [z, ""];
  }, [m]), I = c.useMemo(() => yr(x, mo), [x]), M = c.useMemo(() => v || (p === "uploading" ? `${d || 0}%` : p === "error" ? r.response || Qt : f ? Ma(f) : Qt), [p, d]), [k, R] = c.useMemo(() => {
    for (const {
      ext: z,
      icon: D,
      color: W
    } of Pa)
      if (yr(x, z))
        return [D, W];
    return [/* @__PURE__ */ c.createElement(Ao, {
      key: "defaultIcon"
    }), dn];
  }, [x]), [L, F] = c.useState();
  c.useEffect(() => {
    if (r.originFileObj) {
      let z = !0;
      return Ta(r.originFileObj).then((D) => {
        z && F(D);
      }), () => {
        z = !1;
      };
    }
    F(void 0);
  }, [r.originFileObj]);
  let b = null;
  const w = r.thumbUrl || r.url || L, O = I && (r.originFileObj || w);
  return O ? b = /* @__PURE__ */ c.createElement(c.Fragment, null, w && /* @__PURE__ */ c.createElement(as, ye({
    alt: "preview",
    src: w
  }, a)), p !== "done" && /* @__PURE__ */ c.createElement("div", {
    className: `${y}-img-mask`
  }, p === "uploading" && d !== void 0 && /* @__PURE__ */ c.createElement(Ra, {
    percent: d,
    prefixCls: y
  }), p === "error" && /* @__PURE__ */ c.createElement("div", {
    className: `${y}-desc`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${y}-ellipsis-prefix`
  }, M)))) : b = /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement("div", {
    className: `${y}-icon`,
    style: {
      color: R
    }
  }, k), /* @__PURE__ */ c.createElement("div", {
    className: `${y}-content`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${y}-name`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${y}-ellipsis-prefix`
  }, $ ?? Qt), /* @__PURE__ */ c.createElement("div", {
    className: `${y}-ellipsis-suffix`
  }, x)), /* @__PURE__ */ c.createElement("div", {
    className: `${y}-desc`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${y}-ellipsis-prefix`
  }, M)))), _(/* @__PURE__ */ c.createElement("div", {
    className: N(y, {
      [`${y}-status-${p}`]: p,
      [`${y}-type-preview`]: O,
      [`${y}-type-overview`]: !O
    }, s, C, T),
    style: i,
    ref: t
  }, b, !u && o && /* @__PURE__ */ c.createElement("button", {
    type: "button",
    className: `${y}-remove`,
    onClick: () => {
      o(r);
    }
  }, /* @__PURE__ */ c.createElement(zo, null))));
}
const po = /* @__PURE__ */ c.forwardRef(La), br = 1;
function Na(e) {
  const {
    prefixCls: t,
    items: n,
    onRemove: r,
    overflow: o,
    upload: s,
    listClassName: i,
    listStyle: a,
    itemClassName: l,
    uploadClassName: u,
    uploadStyle: m,
    itemStyle: f,
    imageProps: d
  } = e, p = `${t}-list`, v = c.useRef(null), [h, g] = c.useState(!1), {
    disabled: y
  } = c.useContext(rt);
  c.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [_, C] = c.useState(!1), [T, $] = c.useState(!1), x = () => {
    const R = v.current;
    R && (o === "scrollX" ? (C(Math.abs(R.scrollLeft) >= br), $(R.scrollWidth - R.clientWidth - Math.abs(R.scrollLeft) >= br)) : o === "scrollY" && (C(R.scrollTop !== 0), $(R.scrollHeight - R.clientHeight !== R.scrollTop)));
  };
  c.useEffect(() => {
    x();
  }, [o, n.length]);
  const I = (R) => {
    const L = v.current;
    L && L.scrollTo({
      left: L.scrollLeft + R * L.clientWidth,
      behavior: "smooth"
    });
  }, M = () => {
    I(-1);
  }, k = () => {
    I(1);
  };
  return /* @__PURE__ */ c.createElement("div", {
    className: N(p, {
      [`${p}-overflow-${e.overflow}`]: o,
      [`${p}-overflow-ping-start`]: _,
      [`${p}-overflow-ping-end`]: T
    }, i),
    ref: v,
    onScroll: x,
    style: a
  }, /* @__PURE__ */ c.createElement(ba, {
    keys: n.map((R) => ({
      key: R.uid,
      item: R
    })),
    motionName: `${p}-card-motion`,
    component: !1,
    motionAppear: h,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: R,
    item: L,
    className: F,
    style: b
  }) => /* @__PURE__ */ c.createElement(po, {
    key: R,
    prefixCls: t,
    item: L,
    onRemove: r,
    className: N(F, l),
    imageProps: d,
    style: {
      ...b,
      ...f
    }
  })), !y && /* @__PURE__ */ c.createElement(uo, {
    upload: s
  }, /* @__PURE__ */ c.createElement(ie, {
    className: N(u, `${p}-upload-btn`),
    style: m,
    type: "dashed"
  }, /* @__PURE__ */ c.createElement(Go, {
    className: `${p}-upload-btn-icon`
  }))), o === "scrollX" && /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(ie, {
    size: "small",
    shape: "circle",
    className: `${p}-prev-btn`,
    icon: /* @__PURE__ */ c.createElement(qo, null),
    onClick: M
  }), /* @__PURE__ */ c.createElement(ie, {
    size: "small",
    shape: "circle",
    className: `${p}-next-btn`,
    icon: /* @__PURE__ */ c.createElement(Ko, null),
    onClick: k
  })));
}
function Fa(e, t) {
  const {
    prefixCls: n,
    placeholder: r = {},
    upload: o,
    className: s,
    style: i
  } = e, a = `${n}-placeholder`, l = r || {}, {
    disabled: u
  } = c.useContext(rt), [m, f] = c.useState(!1), d = () => {
    f(!0);
  }, p = (g) => {
    g.currentTarget.contains(g.relatedTarget) || f(!1);
  }, v = () => {
    f(!1);
  }, h = /* @__PURE__ */ c.isValidElement(r) ? r : /* @__PURE__ */ c.createElement(Ce, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ c.createElement($e.Text, {
    className: `${a}-icon`
  }, l.icon), /* @__PURE__ */ c.createElement($e.Title, {
    className: `${a}-title`,
    level: 5
  }, l.title), /* @__PURE__ */ c.createElement($e.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, l.description));
  return /* @__PURE__ */ c.createElement("div", {
    className: N(a, {
      [`${a}-drag-in`]: m,
      [`${a}-disabled`]: u
    }, s),
    onDragEnter: d,
    onDragLeave: p,
    onDrop: v,
    "aria-hidden": u,
    style: i
  }, /* @__PURE__ */ c.createElement(Nr.Dragger, ye({
    showUploadList: !1
  }, o, {
    ref: t,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), h));
}
const Oa = /* @__PURE__ */ c.forwardRef(Fa);
function ja(e, t) {
  const {
    prefixCls: n,
    rootClassName: r,
    rootStyle: o,
    className: s,
    style: i,
    items: a,
    children: l,
    getDropContainer: u,
    placeholder: m,
    onChange: f,
    onRemove: d,
    overflow: p,
    imageProps: v,
    disabled: h,
    classNames: g = {},
    styles: y = {},
    ..._
  } = e, {
    getPrefixCls: C,
    direction: T
  } = Re(), $ = C("attachment", n), x = _t("attachments"), {
    classNames: I,
    styles: M
  } = x, k = c.useRef(null), R = c.useRef(null);
  c.useImperativeHandle(t, () => ({
    nativeElement: k.current,
    upload: (B) => {
      var X, K;
      const G = (K = (X = R.current) == null ? void 0 : X.nativeElement) == null ? void 0 : K.querySelector('input[type="file"]');
      if (G) {
        const ae = new DataTransfer();
        ae.items.add(B), G.files = ae.files, G.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [L, F, b] = fo($), w = N(F, b), [O, z] = Si([], {
    value: a
  }), D = Ne((B) => {
    z(B.fileList), f == null || f(B);
  }), W = {
    ..._,
    fileList: O,
    onChange: D
  }, ne = (B) => Promise.resolve(typeof d == "function" ? d(B) : d).then((G) => {
    if (G === !1)
      return;
    const X = O.filter((K) => K.uid !== B.uid);
    D({
      file: {
        ...B,
        status: "removed"
      },
      fileList: X
    });
  });
  let se;
  const U = (B, G, X) => {
    const K = typeof m == "function" ? m(B) : m;
    return /* @__PURE__ */ c.createElement(Oa, {
      placeholder: K,
      upload: W,
      prefixCls: $,
      className: N(I.placeholder, g.placeholder),
      style: {
        ...M.placeholder,
        ...y.placeholder,
        ...G == null ? void 0 : G.style
      },
      ref: X
    });
  };
  if (l)
    se = /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(uo, {
      upload: W,
      rootClassName: r,
      ref: R
    }, l), /* @__PURE__ */ c.createElement(cr, {
      getDropContainer: u,
      prefixCls: $,
      className: N(w, r)
    }, U("drop")));
  else {
    const B = O.length > 0;
    se = /* @__PURE__ */ c.createElement("div", {
      className: N($, w, {
        [`${$}-rtl`]: T === "rtl"
      }, s, r),
      style: {
        ...o,
        ...i
      },
      dir: T || "ltr",
      ref: k
    }, /* @__PURE__ */ c.createElement(Na, {
      prefixCls: $,
      items: O,
      onRemove: ne,
      overflow: p,
      upload: W,
      listClassName: N(I.list, g.list),
      listStyle: {
        ...M.list,
        ...y.list,
        ...!B && {
          display: "none"
        }
      },
      uploadClassName: N(I.upload, g.upload),
      uploadStyle: {
        ...M.upload,
        ...y.upload
      },
      itemClassName: N(I.item, g.item),
      itemStyle: {
        ...M.item,
        ...y.item
      },
      imageProps: v
    }), U("inline", B ? {
      style: {
        display: "none"
      }
    } : {}, R), /* @__PURE__ */ c.createElement(cr, {
      getDropContainer: u || (() => k.current),
      prefixCls: $,
      className: w
    }, U("drop")));
  }
  return L(/* @__PURE__ */ c.createElement(rt.Provider, {
    value: {
      disabled: h
    }
  }, se));
}
const go = /* @__PURE__ */ c.forwardRef(ja);
go.FileCard = po;
function dt(e) {
  return typeof e == "string";
}
const ka = (e, t, n, r) => {
  const o = P.useRef(""), [s, i] = P.useState(1), a = t && dt(e);
  return Ur(() => {
    !a && dt(e) ? i(e.length) : dt(e) && dt(o.current) && e.indexOf(o.current) !== 0 && i(1), o.current = e;
  }, [e]), P.useEffect(() => {
    if (a && s < e.length) {
      const u = setTimeout(() => {
        i((m) => m + n);
      }, r);
      return () => {
        clearTimeout(u);
      };
    }
  }, [s, t, e]), [a ? e.slice(0, s) : e, a && s < e.length];
};
function Aa(e) {
  return P.useMemo(() => {
    if (!e)
      return [!1, 0, 0, null];
    let t = {
      step: 1,
      interval: 50,
      // set default suffix is empty
      suffix: null
    };
    return typeof e == "object" && (t = {
      ...t,
      ...e
    }), [!0, t.step, t.interval, t.suffix];
  }, [e]);
}
const za = ({
  prefixCls: e
}) => /* @__PURE__ */ c.createElement("span", {
  className: `${e}-dot`
}, /* @__PURE__ */ c.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ c.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ c.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-3"
})), Da = (e) => {
  const {
    componentCls: t,
    paddingSM: n,
    padding: r
  } = e;
  return {
    [t]: {
      [`${t}-content`]: {
        // Shared: filled, outlined, shadow
        "&-filled,&-outlined,&-shadow": {
          padding: `${Ve(n)} ${Ve(r)}`,
          borderRadius: e.borderRadiusLG
        },
        // Filled:
        "&-filled": {
          backgroundColor: e.colorFillContent
        },
        // Outlined:
        "&-outlined": {
          border: `1px solid ${e.colorBorderSecondary}`
        },
        // Shadow:
        "&-shadow": {
          boxShadow: e.boxShadowTertiary
        }
      }
    }
  };
}, Ha = (e) => {
  const {
    componentCls: t,
    fontSize: n,
    lineHeight: r,
    paddingSM: o,
    padding: s,
    calc: i
  } = e, a = i(n).mul(r).div(2).add(o).equal(), l = `${t}-content`;
  return {
    [t]: {
      [l]: {
        // round:
        "&-round": {
          borderRadius: {
            _skip_check_: !0,
            value: a
          },
          paddingInline: i(s).mul(1.25).equal()
        }
      },
      // corner:
      [`&-start ${l}-corner`]: {
        borderStartStartRadius: e.borderRadiusXS
      },
      [`&-end ${l}-corner`]: {
        borderStartEndRadius: e.borderRadiusXS
      }
    }
  };
}, Ba = (e) => {
  const {
    componentCls: t,
    padding: n
  } = e;
  return {
    [`${t}-list`]: {
      display: "flex",
      flexDirection: "column",
      gap: n,
      overflowY: "auto",
      "&::-webkit-scrollbar": {
        width: 8,
        backgroundColor: "transparent"
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: e.colorTextTertiary,
        borderRadius: e.borderRadiusSM
      },
      // For Firefox
      "&": {
        scrollbarWidth: "thin",
        scrollbarColor: `${e.colorTextTertiary} transparent`
      }
    }
  };
}, Wa = new Or("loadingMove", {
  "0%": {
    transform: "translateY(0)"
  },
  "10%": {
    transform: "translateY(4px)"
  },
  "20%": {
    transform: "translateY(0)"
  },
  "30%": {
    transform: "translateY(-4px)"
  },
  "40%": {
    transform: "translateY(0)"
  }
}), Va = new Or("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), Xa = (e) => {
  const {
    componentCls: t,
    fontSize: n,
    lineHeight: r,
    paddingSM: o,
    colorText: s,
    calc: i
  } = e;
  return {
    [t]: {
      display: "flex",
      columnGap: o,
      [`&${t}-end`]: {
        justifyContent: "end",
        flexDirection: "row-reverse",
        [`& ${t}-content-wrapper`]: {
          alignItems: "flex-end"
        }
      },
      [`&${t}-rtl`]: {
        direction: "rtl"
      },
      [`&${t}-typing ${t}-content:last-child::after`]: {
        content: '"|"',
        fontWeight: 900,
        userSelect: "none",
        opacity: 1,
        marginInlineStart: "0.1em",
        animationName: Va,
        animationDuration: "0.8s",
        animationIterationCount: "infinite",
        animationTimingFunction: "linear"
      },
      // ============================ Avatar =============================
      [`& ${t}-avatar`]: {
        display: "inline-flex",
        justifyContent: "center",
        alignSelf: "flex-start"
      },
      // ======================== Header & Footer ========================
      [`& ${t}-header, & ${t}-footer`]: {
        fontSize: n,
        lineHeight: r,
        color: e.colorText
      },
      [`& ${t}-header`]: {
        marginBottom: e.paddingXXS
      },
      [`& ${t}-footer`]: {
        marginTop: o
      },
      // =========================== Content =============================
      [`& ${t}-content-wrapper`]: {
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        minWidth: 0,
        maxWidth: "100%"
      },
      [`& ${t}-content`]: {
        position: "relative",
        boxSizing: "border-box",
        minWidth: 0,
        maxWidth: "100%",
        color: s,
        fontSize: e.fontSize,
        lineHeight: e.lineHeight,
        minHeight: i(o).mul(2).add(i(r).mul(n)).equal(),
        wordBreak: "break-word",
        [`& ${t}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: e.marginXS,
          padding: `0 ${Ve(e.paddingXXS)}`,
          "&-item": {
            backgroundColor: e.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: Wa,
            animationDuration: "2s",
            animationIterationCount: "infinite",
            animationTimingFunction: "linear",
            "&:nth-child(1)": {
              animationDelay: "0s"
            },
            "&:nth-child(2)": {
              animationDelay: "0.2s"
            },
            "&:nth-child(3)": {
              animationDelay: "0.4s"
            }
          }
        }
      }
    }
  };
}, Ua = () => ({}), ho = kt("Bubble", (e) => {
  const t = Ke(e, {});
  return [Xa(t), Ba(t), Da(t), Ha(t)];
}, Ua), vo = /* @__PURE__ */ c.createContext({}), Ga = (e, t) => {
  const {
    prefixCls: n,
    className: r,
    rootClassName: o,
    style: s,
    classNames: i = {},
    styles: a = {},
    avatar: l,
    placement: u = "start",
    loading: m = !1,
    loadingRender: f,
    typing: d,
    content: p = "",
    messageRender: v,
    variant: h = "filled",
    shape: g,
    onTypingComplete: y,
    header: _,
    footer: C,
    _key: T,
    ...$
  } = e, {
    onUpdate: x
  } = c.useContext(vo), I = c.useRef(null);
  c.useImperativeHandle(t, () => ({
    nativeElement: I.current
  }));
  const {
    direction: M,
    getPrefixCls: k
  } = Re(), R = k("bubble", n), L = _t("bubble"), [F, b, w, O] = Aa(d), [z, D] = ka(p, F, b, w);
  c.useEffect(() => {
    x == null || x();
  }, [z]);
  const W = c.useRef(!1);
  c.useEffect(() => {
    !D && !m ? W.current || (W.current = !0, y == null || y()) : W.current = !1;
  }, [D, m]);
  const [ne, se, U] = ho(R), B = N(R, o, L.className, r, se, U, `${R}-${u}`, {
    [`${R}-rtl`]: M === "rtl",
    [`${R}-typing`]: D && !m && !v && !O
  }), G = c.useMemo(() => /* @__PURE__ */ c.isValidElement(l) ? l : /* @__PURE__ */ c.createElement(ls, l), [l]), X = c.useMemo(() => v ? v(z) : z, [z, v]), K = (Se) => typeof Se == "function" ? Se(z, {
    key: T
  }) : Se;
  let ae;
  m ? ae = f ? f() : /* @__PURE__ */ c.createElement(za, {
    prefixCls: R
  }) : ae = /* @__PURE__ */ c.createElement(c.Fragment, null, X, D && O);
  let re = /* @__PURE__ */ c.createElement("div", {
    style: {
      ...L.styles.content,
      ...a.content
    },
    className: N(`${R}-content`, `${R}-content-${h}`, g && `${R}-content-${g}`, L.classNames.content, i.content)
  }, ae);
  return (_ || C) && (re = /* @__PURE__ */ c.createElement("div", {
    className: `${R}-content-wrapper`
  }, _ && /* @__PURE__ */ c.createElement("div", {
    className: N(`${R}-header`, L.classNames.header, i.header),
    style: {
      ...L.styles.header,
      ...a.header
    }
  }, K(_)), re, C && /* @__PURE__ */ c.createElement("div", {
    className: N(`${R}-footer`, L.classNames.footer, i.footer),
    style: {
      ...L.styles.footer,
      ...a.footer
    }
  }, K(C)))), ne(/* @__PURE__ */ c.createElement("div", ye({
    style: {
      ...L.style,
      ...s
    },
    className: B
  }, $, {
    ref: I
  }), l && /* @__PURE__ */ c.createElement("div", {
    style: {
      ...L.styles.avatar,
      ...a.avatar
    },
    className: N(`${R}-avatar`, L.classNames.avatar, i.avatar)
  }, G), re));
}, En = /* @__PURE__ */ c.forwardRef(Ga);
function qa(e, t) {
  const n = P.useCallback((r, o) => typeof t == "function" ? t(r, o) : t ? t[r.role] || {} : {}, [t]);
  return P.useMemo(() => (e || []).map((r, o) => {
    const s = r.key ?? `preset_${o}`;
    return {
      ...n(r, o),
      ...r,
      key: s
    };
  }), [e, n]);
}
const Ka = ({
  _key: e,
  ...t
}, n) => /* @__PURE__ */ P.createElement(En, ye({}, t, {
  _key: e,
  ref: (r) => {
    var o;
    r ? n.current[e] = r : (o = n.current) == null || delete o[e];
  }
})), Ya = /* @__PURE__ */ P.memo(/* @__PURE__ */ P.forwardRef(Ka)), Za = 1, Qa = (e, t) => {
  const {
    prefixCls: n,
    rootClassName: r,
    className: o,
    items: s,
    autoScroll: i = !0,
    roles: a,
    onScroll: l,
    ...u
  } = e, m = ci(u, {
    attr: !0,
    aria: !0
  }), f = P.useRef(null), d = P.useRef({}), {
    getPrefixCls: p
  } = Re(), v = p("bubble", n), h = `${v}-list`, [g, y, _] = ho(v), [C, T] = P.useState(!1);
  P.useEffect(() => (T(!0), () => {
    T(!1);
  }), []);
  const $ = qa(s, a), [x, I] = P.useState(!0), [M, k] = P.useState(0), R = (b) => {
    const w = b.target;
    I(w.scrollHeight - Math.abs(w.scrollTop) - w.clientHeight <= Za), l == null || l(b);
  };
  P.useEffect(() => {
    i && f.current && x && f.current.scrollTo({
      top: f.current.scrollHeight
    });
  }, [M]), P.useEffect(() => {
    var b;
    if (i) {
      const w = (b = $[$.length - 2]) == null ? void 0 : b.key, O = d.current[w];
      if (O) {
        const {
          nativeElement: z
        } = O, {
          top: D,
          bottom: W
        } = z.getBoundingClientRect(), {
          top: ne,
          bottom: se
        } = f.current.getBoundingClientRect();
        D < se && W > ne && (k((B) => B + 1), I(!0));
      }
    }
  }, [$.length]), P.useImperativeHandle(t, () => ({
    nativeElement: f.current,
    scrollTo: ({
      key: b,
      offset: w,
      behavior: O = "smooth",
      block: z
    }) => {
      if (typeof w == "number")
        f.current.scrollTo({
          top: w,
          behavior: O
        });
      else if (b !== void 0) {
        const D = d.current[b];
        if (D) {
          const W = $.findIndex((ne) => ne.key === b);
          I(W === $.length - 1), D.nativeElement.scrollIntoView({
            behavior: O,
            block: z
          });
        }
      }
    }
  }));
  const L = Ne(() => {
    i && k((b) => b + 1);
  }), F = P.useMemo(() => ({
    onUpdate: L
  }), []);
  return g(/* @__PURE__ */ P.createElement(vo.Provider, {
    value: F
  }, /* @__PURE__ */ P.createElement("div", ye({}, m, {
    className: N(h, r, o, y, _, {
      [`${h}-reach-end`]: x
    }),
    ref: f,
    onScroll: R
  }), $.map(({
    key: b,
    ...w
  }) => /* @__PURE__ */ P.createElement(Ya, ye({}, w, {
    key: b,
    _key: b,
    ref: d,
    typing: C ? w.typing : !1
  }))))));
}, Ja = /* @__PURE__ */ P.forwardRef(Qa);
En.List = Ja;
const el = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ======================== Prompt ========================
      "&, & *": {
        boxSizing: "border-box"
      },
      maxWidth: "100%",
      [`&${t}-rtl`]: {
        direction: "rtl"
      },
      [`& ${t}-title`]: {
        marginBlockStart: 0,
        fontWeight: "normal",
        color: e.colorTextTertiary
      },
      [`& ${t}-list`]: {
        display: "flex",
        gap: e.paddingSM,
        overflowX: "auto",
        // Hide scrollbar
        scrollbarWidth: "none",
        "-ms-overflow-style": "none",
        "&::-webkit-scrollbar": {
          display: "none"
        },
        listStyle: "none",
        paddingInlineStart: 0,
        marginBlock: 0,
        alignItems: "stretch",
        "&-wrap": {
          flexWrap: "wrap"
        },
        "&-vertical": {
          flexDirection: "column",
          alignItems: "flex-start"
        }
      },
      // ========================= Item =========================
      [`${t}-item`]: {
        flex: "none",
        display: "flex",
        gap: e.paddingXS,
        height: "auto",
        paddingBlock: e.paddingSM,
        paddingInline: e.padding,
        alignItems: "flex-start",
        justifyContent: "flex-start",
        background: e.colorBgContainer,
        borderRadius: e.borderRadiusLG,
        transition: ["border", "background"].map((n) => `${n} ${e.motionDurationSlow}`).join(","),
        border: `${Ve(e.lineWidth)} ${e.lineType} ${e.colorBorderSecondary}`,
        [`&:not(${t}-item-has-nest)`]: {
          "&:hover": {
            cursor: "pointer",
            background: e.colorFillTertiary
          },
          "&:active": {
            background: e.colorFill
          }
        },
        [`${t}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          gap: e.paddingXXS,
          flexDirection: "column",
          alignItems: "flex-start"
        },
        [`${t}-icon, ${t}-label, ${t}-desc`]: {
          margin: 0,
          padding: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight,
          textAlign: "start",
          whiteSpace: "normal"
        },
        [`${t}-label`]: {
          color: e.colorTextHeading,
          fontWeight: 500
        },
        [`${t}-label + ${t}-desc`]: {
          color: e.colorTextTertiary
        },
        // Disabled
        [`&${t}-item-disabled`]: {
          pointerEvents: "none",
          background: e.colorBgContainerDisabled,
          [`${t}-label, ${t}-desc`]: {
            color: e.colorTextTertiary
          }
        }
      }
    }
  };
}, tl = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ========================= Parent =========================
      [`${t}-item-has-nest`]: {
        [`> ${t}-content`]: {
          // gap: token.paddingSM,
          [`> ${t}-label`]: {
            fontSize: e.fontSizeLG,
            lineHeight: e.lineHeightLG
          }
        }
      },
      // ========================= Nested =========================
      [`&${t}-nested`]: {
        marginTop: e.paddingXS,
        // ======================== Prompt ========================
        alignSelf: "stretch",
        [`${t}-list`]: {
          alignItems: "stretch"
        },
        // ========================= Item =========================
        [`${t}-item`]: {
          border: 0,
          background: e.colorFillQuaternary
        }
      }
    }
  };
}, nl = () => ({}), rl = kt("Prompts", (e) => {
  const t = Ke(e, {});
  return [el(t), tl(t)];
}, nl), Cn = (e) => {
  const {
    prefixCls: t,
    title: n,
    className: r,
    items: o,
    onItemClick: s,
    vertical: i,
    wrap: a,
    rootClassName: l,
    styles: u = {},
    classNames: m = {},
    style: f,
    ...d
  } = e, {
    getPrefixCls: p,
    direction: v
  } = Re(), h = p("prompts", t), g = _t("prompts"), [y, _, C] = rl(h), T = N(h, g.className, r, l, _, C, {
    [`${h}-rtl`]: v === "rtl"
  }), $ = N(`${h}-list`, g.classNames.list, m.list, {
    [`${h}-list-wrap`]: a
  }, {
    [`${h}-list-vertical`]: i
  });
  return y(/* @__PURE__ */ c.createElement("div", ye({}, d, {
    className: T,
    style: {
      ...f,
      ...g.style
    }
  }), n && /* @__PURE__ */ c.createElement($e.Title, {
    level: 5,
    className: N(`${h}-title`, g.classNames.title, m.title),
    style: {
      ...g.styles.title,
      ...u.title
    }
  }, n), /* @__PURE__ */ c.createElement("div", {
    className: $,
    style: {
      ...g.styles.list,
      ...u.list
    }
  }, o == null ? void 0 : o.map((x, I) => {
    const M = x.children && x.children.length > 0;
    return /* @__PURE__ */ c.createElement("div", {
      key: x.key || `key_${I}`,
      style: {
        ...g.styles.item,
        ...u.item
      },
      className: N(`${h}-item`, g.classNames.item, m.item, {
        [`${h}-item-disabled`]: x.disabled,
        [`${h}-item-has-nest`]: M
      }),
      onClick: () => {
        !M && s && s({
          data: x
        });
      }
    }, x.icon && /* @__PURE__ */ c.createElement("div", {
      className: `${h}-icon`
    }, x.icon), /* @__PURE__ */ c.createElement("div", {
      className: N(`${h}-content`, g.classNames.itemContent, m.itemContent),
      style: {
        ...g.styles.itemContent,
        ...u.itemContent
      }
    }, x.label && /* @__PURE__ */ c.createElement("h6", {
      className: `${h}-label`
    }, x.label), x.description && /* @__PURE__ */ c.createElement("p", {
      className: `${h}-desc`
    }, x.description), M && /* @__PURE__ */ c.createElement(Cn, {
      className: `${h}-nested`,
      items: x.children,
      vertical: !0,
      onItemClick: s,
      classNames: {
        list: m.subList,
        item: m.subItem
      },
      styles: {
        list: u.subList,
        item: u.subItem
      }
    })));
  }))));
}, ol = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, r = n(e.fontSizeHeading3).mul(e.lineHeightHeading3).equal(), o = n(e.fontSize).mul(e.lineHeight).equal();
  return {
    [t]: {
      gap: e.padding,
      // ======================== Icon ========================
      [`${t}-icon`]: {
        height: n(r).add(o).add(e.paddingXXS).equal(),
        display: "flex",
        img: {
          height: "100%"
        }
      },
      // ==================== Content Wrap ====================
      [`${t}-content-wrapper`]: {
        gap: e.paddingXS,
        flex: "auto",
        minWidth: 0,
        [`${t}-title-wrapper`]: {
          gap: e.paddingXS
        },
        [`${t}-title`]: {
          margin: 0
        },
        [`${t}-extra`]: {
          marginInlineStart: "auto"
        }
      }
    }
  };
}, sl = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ======================== Filled ========================
      "&-filled": {
        paddingInline: e.padding,
        paddingBlock: e.paddingSM,
        background: e.colorFillContent,
        borderRadius: e.borderRadiusLG
      },
      // ====================== Borderless ======================
      "&-borderless": {
        [`${t}-title`]: {
          fontSize: e.fontSizeHeading3,
          lineHeight: e.lineHeightHeading3
        }
      }
    }
  };
}, il = () => ({}), al = kt("Welcome", (e) => {
  const t = Ke(e, {});
  return [ol(t), sl(t)];
}, il);
function ll(e, t) {
  const {
    prefixCls: n,
    rootClassName: r,
    className: o,
    style: s,
    variant: i = "filled",
    // Semantic
    classNames: a = {},
    styles: l = {},
    // Layout
    icon: u,
    title: m,
    description: f,
    extra: d
  } = e, {
    direction: p,
    getPrefixCls: v
  } = Re(), h = v("welcome", n), g = _t("welcome"), [y, _, C] = al(h), T = c.useMemo(() => {
    if (!u)
      return null;
    let I = u;
    return typeof u == "string" && u.startsWith("http") && (I = /* @__PURE__ */ c.createElement("img", {
      src: u,
      alt: "icon"
    })), /* @__PURE__ */ c.createElement("div", {
      className: N(`${h}-icon`, g.classNames.icon, a.icon),
      style: l.icon
    }, I);
  }, [u]), $ = c.useMemo(() => m ? /* @__PURE__ */ c.createElement($e.Title, {
    level: 4,
    className: N(`${h}-title`, g.classNames.title, a.title),
    style: l.title
  }, m) : null, [m]), x = c.useMemo(() => d ? /* @__PURE__ */ c.createElement("div", {
    className: N(`${h}-extra`, g.classNames.extra, a.extra),
    style: l.extra
  }, d) : null, [d]);
  return y(/* @__PURE__ */ c.createElement(Ce, {
    ref: t,
    className: N(h, g.className, o, r, _, C, `${h}-${i}`, {
      [`${h}-rtl`]: p === "rtl"
    }),
    style: s
  }, T, /* @__PURE__ */ c.createElement(Ce, {
    vertical: !0,
    className: `${h}-content-wrapper`
  }, d ? /* @__PURE__ */ c.createElement(Ce, {
    align: "flex-start",
    className: `${h}-title-wrapper`
  }, $, x) : $, f && /* @__PURE__ */ c.createElement($e.Text, {
    className: N(`${h}-description`, g.classNames.description, a.description),
    style: l.description
  }, f))));
}
const cl = /* @__PURE__ */ c.forwardRef(ll);
function oe(e) {
  const t = J(e);
  return t.current = e, Lo((...n) => {
    var r;
    return (r = t.current) == null ? void 0 : r.call(t, ...n);
  }, []);
}
function be(e, t) {
  return Object.keys(e).reduce((n, r) => (e[r] !== void 0 && (!(t != null && t.omitNull) || e[r] !== null) && (n[r] = e[r]), n), {});
}
var yo = Symbol.for("immer-nothing"), xr = Symbol.for("immer-draftable"), ce = Symbol.for("immer-state");
function he(e, ...t) {
  throw new Error(`[Immer] minified error nr: ${e}. Full error at: https://bit.ly/3cXEKWf`);
}
var Xe = Object.getPrototypeOf;
function Ue(e) {
  return !!e && !!e[ce];
}
function Fe(e) {
  var t;
  return e ? bo(e) || Array.isArray(e) || !!e[xr] || !!((t = e.constructor) != null && t[xr]) || zt(e) || Dt(e) : !1;
}
var ul = Object.prototype.constructor.toString();
function bo(e) {
  if (!e || typeof e != "object") return !1;
  const t = Xe(e);
  if (t === null)
    return !0;
  const n = Object.hasOwnProperty.call(t, "constructor") && t.constructor;
  return n === Object ? !0 : typeof n == "function" && Function.toString.call(n) === ul;
}
function bt(e, t) {
  At(e) === 0 ? Reflect.ownKeys(e).forEach((n) => {
    t(n, e[n], e);
  }) : e.forEach((n, r) => t(r, n, e));
}
function At(e) {
  const t = e[ce];
  return t ? t.type_ : Array.isArray(e) ? 1 : zt(e) ? 2 : Dt(e) ? 3 : 0;
}
function fn(e, t) {
  return At(e) === 2 ? e.has(t) : Object.prototype.hasOwnProperty.call(e, t);
}
function xo(e, t, n) {
  const r = At(e);
  r === 2 ? e.set(t, n) : r === 3 ? e.add(n) : e[t] = n;
}
function dl(e, t) {
  return e === t ? e !== 0 || 1 / e === 1 / t : e !== e && t !== t;
}
function zt(e) {
  return e instanceof Map;
}
function Dt(e) {
  return e instanceof Set;
}
function Me(e) {
  return e.copy_ || e.base_;
}
function mn(e, t) {
  if (zt(e))
    return new Map(e);
  if (Dt(e))
    return new Set(e);
  if (Array.isArray(e)) return Array.prototype.slice.call(e);
  const n = bo(e);
  if (t === !0 || t === "class_only" && !n) {
    const r = Object.getOwnPropertyDescriptors(e);
    delete r[ce];
    let o = Reflect.ownKeys(r);
    for (let s = 0; s < o.length; s++) {
      const i = o[s], a = r[i];
      a.writable === !1 && (a.writable = !0, a.configurable = !0), (a.get || a.set) && (r[i] = {
        configurable: !0,
        writable: !0,
        // could live with !!desc.set as well here...
        enumerable: a.enumerable,
        value: e[i]
      });
    }
    return Object.create(Xe(e), r);
  } else {
    const r = Xe(e);
    if (r !== null && n)
      return {
        ...e
      };
    const o = Object.create(r);
    return Object.assign(o, e);
  }
}
function Tn(e, t = !1) {
  return Ht(e) || Ue(e) || !Fe(e) || (At(e) > 1 && (e.set = e.add = e.clear = e.delete = fl), Object.freeze(e), t && Object.entries(e).forEach(([n, r]) => Tn(r, !0))), e;
}
function fl() {
  he(2);
}
function Ht(e) {
  return Object.isFrozen(e);
}
var ml = {};
function Oe(e) {
  const t = ml[e];
  return t || he(0, e), t;
}
var et;
function So() {
  return et;
}
function pl(e, t) {
  return {
    drafts_: [],
    parent_: e,
    immer_: t,
    // Whenever the modified draft contains a draft from another scope, we
    // need to prevent auto-freezing so the unowned draft can be finalized.
    canAutoFreeze_: !0,
    unfinalizedDrafts_: 0
  };
}
function Sr(e, t) {
  t && (Oe("Patches"), e.patches_ = [], e.inversePatches_ = [], e.patchListener_ = t);
}
function pn(e) {
  gn(e), e.drafts_.forEach(gl), e.drafts_ = null;
}
function gn(e) {
  e === et && (et = e.parent_);
}
function wr(e) {
  return et = pl(et, e);
}
function gl(e) {
  const t = e[ce];
  t.type_ === 0 || t.type_ === 1 ? t.revoke_() : t.revoked_ = !0;
}
function _r(e, t) {
  t.unfinalizedDrafts_ = t.drafts_.length;
  const n = t.drafts_[0];
  return e !== void 0 && e !== n ? (n[ce].modified_ && (pn(t), he(4)), Fe(e) && (e = xt(t, e), t.parent_ || St(t, e)), t.patches_ && Oe("Patches").generateReplacementPatches_(n[ce].base_, e, t.patches_, t.inversePatches_)) : e = xt(t, n, []), pn(t), t.patches_ && t.patchListener_(t.patches_, t.inversePatches_), e !== yo ? e : void 0;
}
function xt(e, t, n) {
  if (Ht(t)) return t;
  const r = t[ce];
  if (!r)
    return bt(t, (o, s) => Er(e, r, t, o, s, n)), t;
  if (r.scope_ !== e) return t;
  if (!r.modified_)
    return St(e, r.base_, !0), r.base_;
  if (!r.finalized_) {
    r.finalized_ = !0, r.scope_.unfinalizedDrafts_--;
    const o = r.copy_;
    let s = o, i = !1;
    r.type_ === 3 && (s = new Set(o), o.clear(), i = !0), bt(s, (a, l) => Er(e, r, o, a, l, n, i)), St(e, o, !1), n && e.patches_ && Oe("Patches").generatePatches_(r, n, e.patches_, e.inversePatches_);
  }
  return r.copy_;
}
function Er(e, t, n, r, o, s, i) {
  if (Ue(o)) {
    const a = s && t && t.type_ !== 3 && // Set objects are atomic since they have no keys.
    !fn(t.assigned_, r) ? s.concat(r) : void 0, l = xt(e, o, a);
    if (xo(n, r, l), Ue(l))
      e.canAutoFreeze_ = !1;
    else return;
  } else i && n.add(o);
  if (Fe(o) && !Ht(o)) {
    if (!e.immer_.autoFreeze_ && e.unfinalizedDrafts_ < 1)
      return;
    xt(e, o), (!t || !t.scope_.parent_) && typeof r != "symbol" && Object.prototype.propertyIsEnumerable.call(n, r) && St(e, o);
  }
}
function St(e, t, n = !1) {
  !e.parent_ && e.immer_.autoFreeze_ && e.canAutoFreeze_ && Tn(t, n);
}
function hl(e, t) {
  const n = Array.isArray(e), r = {
    type_: n ? 1 : 0,
    // Track which produce call this is associated with.
    scope_: t ? t.scope_ : So(),
    // True for both shallow and deep changes.
    modified_: !1,
    // Used during finalization.
    finalized_: !1,
    // Track which properties have been assigned (true) or deleted (false).
    assigned_: {},
    // The parent draft state.
    parent_: t,
    // The base state.
    base_: e,
    // The base proxy.
    draft_: null,
    // set below
    // The base copy with any updated values.
    copy_: null,
    // Called by the `produce` function.
    revoke_: null,
    isManual_: !1
  };
  let o = r, s = $n;
  n && (o = [r], s = tt);
  const {
    revoke: i,
    proxy: a
  } = Proxy.revocable(o, s);
  return r.draft_ = a, r.revoke_ = i, a;
}
var $n = {
  get(e, t) {
    if (t === ce) return e;
    const n = Me(e);
    if (!fn(n, t))
      return vl(e, n, t);
    const r = n[t];
    return e.finalized_ || !Fe(r) ? r : r === Jt(e.base_, t) ? (en(e), e.copy_[t] = vn(r, e)) : r;
  },
  has(e, t) {
    return t in Me(e);
  },
  ownKeys(e) {
    return Reflect.ownKeys(Me(e));
  },
  set(e, t, n) {
    const r = wo(Me(e), t);
    if (r != null && r.set)
      return r.set.call(e.draft_, n), !0;
    if (!e.modified_) {
      const o = Jt(Me(e), t), s = o == null ? void 0 : o[ce];
      if (s && s.base_ === n)
        return e.copy_[t] = n, e.assigned_[t] = !1, !0;
      if (dl(n, o) && (n !== void 0 || fn(e.base_, t))) return !0;
      en(e), hn(e);
    }
    return e.copy_[t] === n && // special case: handle new props with value 'undefined'
    (n !== void 0 || t in e.copy_) || // special case: NaN
    Number.isNaN(n) && Number.isNaN(e.copy_[t]) || (e.copy_[t] = n, e.assigned_[t] = !0), !0;
  },
  deleteProperty(e, t) {
    return Jt(e.base_, t) !== void 0 || t in e.base_ ? (e.assigned_[t] = !1, en(e), hn(e)) : delete e.assigned_[t], e.copy_ && delete e.copy_[t], !0;
  },
  // Note: We never coerce `desc.value` into an Immer draft, because we can't make
  // the same guarantee in ES5 mode.
  getOwnPropertyDescriptor(e, t) {
    const n = Me(e), r = Reflect.getOwnPropertyDescriptor(n, t);
    return r && {
      writable: !0,
      configurable: e.type_ !== 1 || t !== "length",
      enumerable: r.enumerable,
      value: n[t]
    };
  },
  defineProperty() {
    he(11);
  },
  getPrototypeOf(e) {
    return Xe(e.base_);
  },
  setPrototypeOf() {
    he(12);
  }
}, tt = {};
bt($n, (e, t) => {
  tt[e] = function() {
    return arguments[0] = arguments[0][0], t.apply(this, arguments);
  };
});
tt.deleteProperty = function(e, t) {
  return tt.set.call(this, e, t, void 0);
};
tt.set = function(e, t, n) {
  return $n.set.call(this, e[0], t, n, e[0]);
};
function Jt(e, t) {
  const n = e[ce];
  return (n ? Me(n) : e)[t];
}
function vl(e, t, n) {
  var o;
  const r = wo(t, n);
  return r ? "value" in r ? r.value : (
    // This is a very special case, if the prop is a getter defined by the
    // prototype, we should invoke it with the draft as context!
    (o = r.get) == null ? void 0 : o.call(e.draft_)
  ) : void 0;
}
function wo(e, t) {
  if (!(t in e)) return;
  let n = Xe(e);
  for (; n; ) {
    const r = Object.getOwnPropertyDescriptor(n, t);
    if (r) return r;
    n = Xe(n);
  }
}
function hn(e) {
  e.modified_ || (e.modified_ = !0, e.parent_ && hn(e.parent_));
}
function en(e) {
  e.copy_ || (e.copy_ = mn(e.base_, e.scope_.immer_.useStrictShallowCopy_));
}
var yl = class {
  constructor(e) {
    this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.produce = (t, n, r) => {
      if (typeof t == "function" && typeof n != "function") {
        const s = n;
        n = t;
        const i = this;
        return function(l = s, ...u) {
          return i.produce(l, (m) => n.call(this, m, ...u));
        };
      }
      typeof n != "function" && he(6), r !== void 0 && typeof r != "function" && he(7);
      let o;
      if (Fe(t)) {
        const s = wr(this), i = vn(t, void 0);
        let a = !0;
        try {
          o = n(i), a = !1;
        } finally {
          a ? pn(s) : gn(s);
        }
        return Sr(s, r), _r(o, s);
      } else if (!t || typeof t != "object") {
        if (o = n(t), o === void 0 && (o = t), o === yo && (o = void 0), this.autoFreeze_ && Tn(o, !0), r) {
          const s = [], i = [];
          Oe("Patches").generateReplacementPatches_(t, o, s, i), r(s, i);
        }
        return o;
      } else he(1, t);
    }, this.produceWithPatches = (t, n) => {
      if (typeof t == "function")
        return (i, ...a) => this.produceWithPatches(i, (l) => t(l, ...a));
      let r, o;
      return [this.produce(t, n, (i, a) => {
        r = i, o = a;
      }), r, o];
    }, typeof (e == null ? void 0 : e.autoFreeze) == "boolean" && this.setAutoFreeze(e.autoFreeze), typeof (e == null ? void 0 : e.useStrictShallowCopy) == "boolean" && this.setUseStrictShallowCopy(e.useStrictShallowCopy);
  }
  createDraft(e) {
    Fe(e) || he(8), Ue(e) && (e = bl(e));
    const t = wr(this), n = vn(e, void 0);
    return n[ce].isManual_ = !0, gn(t), n;
  }
  finishDraft(e, t) {
    const n = e && e[ce];
    (!n || !n.isManual_) && he(9);
    const {
      scope_: r
    } = n;
    return Sr(r, t), _r(void 0, r);
  }
  /**
   * Pass true to automatically freeze all copies created by Immer.
   *
   * By default, auto-freezing is enabled.
   */
  setAutoFreeze(e) {
    this.autoFreeze_ = e;
  }
  /**
   * Pass true to enable strict shallow copy.
   *
   * By default, immer does not copy the object descriptors such as getter, setter and non-enumrable properties.
   */
  setUseStrictShallowCopy(e) {
    this.useStrictShallowCopy_ = e;
  }
  applyPatches(e, t) {
    let n;
    for (n = t.length - 1; n >= 0; n--) {
      const o = t[n];
      if (o.path.length === 0 && o.op === "replace") {
        e = o.value;
        break;
      }
    }
    n > -1 && (t = t.slice(n + 1));
    const r = Oe("Patches").applyPatches_;
    return Ue(e) ? r(e, t) : this.produce(e, (o) => r(o, t));
  }
};
function vn(e, t) {
  const n = zt(e) ? Oe("MapSet").proxyMap_(e, t) : Dt(e) ? Oe("MapSet").proxySet_(e, t) : hl(e, t);
  return (t ? t.scope_ : So()).drafts_.push(n), n;
}
function bl(e) {
  return Ue(e) || he(10, e), _o(e);
}
function _o(e) {
  if (!Fe(e) || Ht(e)) return e;
  const t = e[ce];
  let n;
  if (t) {
    if (!t.modified_) return t.base_;
    t.finalized_ = !0, n = mn(e, t.scope_.immer_.useStrictShallowCopy_);
  } else
    n = mn(e, !0);
  return bt(n, (r, o) => {
    xo(n, r, _o(o));
  }), t && (t.finalized_ = !1), n;
}
var ue = new yl(), Cr = ue.produce;
ue.produceWithPatches.bind(ue);
ue.setAutoFreeze.bind(ue);
ue.setUseStrictShallowCopy.bind(ue);
ue.applyPatches.bind(ue);
ue.createDraft.bind(ue);
ue.finishDraft.bind(ue);
const {
  useItems: ic,
  withItemsContextProvider: ac,
  ItemHandler: lc
} = Fr("antdx-bubble.list-items"), {
  useItems: xl,
  withItemsContextProvider: Sl,
  ItemHandler: cc
} = Fr("antdx-bubble.list-roles");
function wl(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function _l(e, t = !1) {
  try {
    if (bn(e))
      return e;
    if (t && !wl(e))
      return;
    if (typeof e == "string") {
      let n = e.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function El(e, t) {
  return fe(() => _l(e, t), [e, t]);
}
function Cl(e, t) {
  return t((r, o) => bn(r) ? o ? (...s) => ve(o) && o.unshift ? r(...e, ...s) : r(...s, ...e) : r(...e) : r);
}
const Tl = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $l(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const r = e[n];
    return t[n] = Rl(n, r), t;
  }, {}) : {};
}
function Rl(e, t) {
  return typeof t == "number" && !Tl.includes(e) ? t + "px" : t;
}
function yn(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const o = c.Children.toArray(e._reactElement.props.children).map((s) => {
      if (c.isValidElement(s) && s.props.__slot__) {
        const {
          portals: i,
          clonedElement: a
        } = yn(s.props.el);
        return c.cloneElement(s, {
          ...s.props,
          el: a,
          children: [...c.Children.toArray(s.props.children), ...i]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(ht(c.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: i,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, i, l);
    });
  });
  const r = Array.from(e.childNodes);
  for (let o = 0; o < r.length; o++) {
    const s = r[o];
    if (s.nodeType === 1) {
      const {
        clonedElement: i,
        portals: a
      } = yn(s);
      t.push(...a), n.appendChild(i);
    } else s.nodeType === 3 && n.appendChild(s.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Il(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Tr = No(({
  slot: e,
  clone: t,
  className: n,
  style: r,
  observeAttributes: o
}, s) => {
  const i = J(), [a, l] = Ze([]), {
    forceClone: u
  } = ms(), m = u ? !0 : t;
  return Ee(() => {
    var h;
    if (!i.current || !e)
      return;
    let f = e;
    function d() {
      let g = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (g = f.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Il(s, g), n && g.classList.add(...n.split(" ")), r) {
        const y = $l(r);
        Object.keys(y).forEach((_) => {
          g.style[_] = y[_];
        });
      }
    }
    let p = null, v = null;
    if (m && window.MutationObserver) {
      let g = function() {
        var T, $, x;
        (T = i.current) != null && T.contains(f) && (($ = i.current) == null || $.removeChild(f));
        const {
          portals: _,
          clonedElement: C
        } = yn(e);
        f = C, l(_), f.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          d();
        }, 50), (x = i.current) == null || x.appendChild(f);
      };
      g();
      const y = Rs(() => {
        g(), p == null || p.disconnect(), p == null || p.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      p = new window.MutationObserver(y), p.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", d(), (h = i.current) == null || h.appendChild(f);
    return () => {
      var g, y;
      f.style.display = "", (g = i.current) != null && g.contains(f) && ((y = i.current) == null || y.removeChild(f)), p == null || p.disconnect();
    };
  }, [e, m, n, r, s, o, u]), c.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...a);
}), Pl = ({
  children: e,
  ...t
}) => /* @__PURE__ */ S.jsx(S.Fragment, {
  children: e(t)
});
function Ml(e) {
  return c.createElement(Pl, {
    children: e
  });
}
function Eo(e, t, n) {
  const r = e.filter(Boolean);
  if (r.length !== 0)
    return r.map((o, s) => {
      var u, m;
      if (typeof o != "object")
        return t != null && t.fallback ? t.fallback(o) : o;
      const i = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...o.props,
        key: ((u = o.props) == null ? void 0 : u.key) ?? (n ? `${n}-${s}` : `${s}`)
      }) : {
        ...o.props,
        key: ((m = o.props) == null ? void 0 : m.key) ?? (n ? `${n}-${s}` : `${s}`)
      };
      let a = i;
      Object.keys(o.slots).forEach((f) => {
        if (!o.slots[f] || !(o.slots[f] instanceof Element) && !o.slots[f].el)
          return;
        const d = f.split(".");
        d.forEach((_, C) => {
          a[_] || (a[_] = {}), C !== d.length - 1 && (a = i[_]);
        });
        const p = o.slots[f];
        let v, h, g = (t == null ? void 0 : t.clone) ?? !1, y = t == null ? void 0 : t.forceClone;
        p instanceof Element ? v = p : (v = p.el, h = p.callback, g = p.clone ?? g, y = p.forceClone ?? y), y = y ?? !!h, a[d[d.length - 1]] = v ? h ? (..._) => (h(d[d.length - 1], _), /* @__PURE__ */ S.jsx(zn, {
          ...o.ctx,
          params: _,
          forceClone: y,
          children: /* @__PURE__ */ S.jsx(Tr, {
            slot: v,
            clone: g
          })
        })) : Ml((_) => /* @__PURE__ */ S.jsx(zn, {
          ...o.ctx,
          forceClone: y,
          children: /* @__PURE__ */ S.jsx(Tr, {
            ..._,
            slot: v,
            clone: g
          })
        })) : a[d[d.length - 1]], a = i;
      });
      const l = (t == null ? void 0 : t.children) || "children";
      return o[l] ? i[l] = Eo(o[l], t, `${s}`) : t != null && t.children && (i[l] = void 0, Reflect.deleteProperty(i, l)), i;
    });
}
const Co = Symbol();
function Ll(e, t) {
  return Cl(t, (n) => {
    var r, o;
    return {
      ...e,
      avatar: bn(e.avatar) ? n(e.avatar) : ve(e.avatar) ? {
        ...e.avatar,
        icon: n((r = e.avatar) == null ? void 0 : r.icon),
        src: n((o = e.avatar) == null ? void 0 : o.src)
      } : e.avatar,
      footer: n(e.footer, {
        unshift: !0
      }),
      header: n(e.header, {
        unshift: !0
      }),
      loadingRender: n(e.loadingRender, !0),
      messageRender: n(e.messageRender, !0)
    };
  });
}
function Nl({
  roles: e,
  preProcess: t,
  postProcess: n
}, r = []) {
  const o = El(e), s = oe(t), i = oe(n), {
    items: {
      roles: a
    }
  } = xl(), l = fe(() => {
    var m;
    return e || ((m = Eo(a, {
      clone: !0,
      forceClone: !0
    })) == null ? void 0 : m.reduce((f, d) => (d.role !== void 0 && (f[d.role] = d), f), {}));
  }, [a, e]), u = fe(() => (m, f) => {
    const d = f ?? m[Co], p = s(m, d) || m;
    if (p.role && (l || {})[p.role])
      return Ll((l || {})[p.role], [p, d]);
    let v;
    return v = i(p, d), v || {
      messageRender(h) {
        return /* @__PURE__ */ S.jsx(S.Fragment, {
          children: ve(h) ? JSON.stringify(h) : h
        });
      }
    };
  }, [l, i, s, ...r]);
  return o || u;
}
function Fl(e) {
  const [t, n] = Ze(!1), r = J(0), o = J(!0), s = J(!0), {
    autoScroll: i,
    scrollButtonOffset: a,
    ref: l,
    value: u
  } = e, m = oe((d = "instant") => {
    l.current && (s.current = !0, requestAnimationFrame(() => {
      var p;
      (p = l.current) == null || p.scrollTo({
        offset: l.current.nativeElement.scrollHeight,
        behavior: d
      });
    }), n(!1));
  }), f = oe((d = 100) => {
    if (!l.current)
      return !1;
    const p = l.current.nativeElement, v = p.scrollHeight, {
      scrollTop: h,
      clientHeight: g
    } = p;
    return v - (h + g) < d;
  });
  return Ee(() => {
    l.current && i && (u.length !== r.current && (o.current = !0), o.current && requestAnimationFrame(() => {
      m();
    }), r.current = u.length);
  }, [u, l, i, m, f]), Ee(() => {
    if (l.current && i) {
      const d = l.current.nativeElement;
      let p = 0, v = 0;
      const h = (g) => {
        const y = g.target;
        s.current ? s.current = !1 : y.scrollTop < p && y.scrollHeight >= v ? o.current = !1 : f() && (o.current = !0), p = y.scrollTop, v = y.scrollHeight, n(!f(a));
      };
      return d.addEventListener("scroll", h), () => {
        d.removeEventListener("scroll", h);
      };
    }
  }, [i, f, a]), {
    showScrollButton: t,
    scrollToBottom: m
  };
}
new Intl.Collator(0, {
  numeric: 1
}).compare;
typeof process < "u" && process.versions && process.versions.node;
var _e;
class uc extends TransformStream {
  /** Constructs a new instance. */
  constructor(n = {
    allowCR: !1
  }) {
    super({
      transform: (r, o) => {
        for (r = De(this, _e) + r; ; ) {
          const s = r.indexOf(`
`), i = n.allowCR ? r.indexOf("\r") : -1;
          if (i !== -1 && i !== r.length - 1 && (s === -1 || s - 1 > i)) {
            o.enqueue(r.slice(0, i)), r = r.slice(i + 1);
            continue;
          }
          if (s === -1) break;
          const a = r[s - 1] === "\r" ? s - 1 : s;
          o.enqueue(r.slice(0, a)), r = r.slice(s + 1);
        }
        jn(this, _e, r);
      },
      flush: (r) => {
        if (De(this, _e) === "") return;
        const o = n.allowCR && De(this, _e).endsWith("\r") ? De(this, _e).slice(0, -1) : De(this, _e);
        r.enqueue(o);
      }
    });
    On(this, _e, "");
  }
}
_e = new WeakMap();
function Ol(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function jl() {
  const e = document.querySelector(".gradio-container");
  if (!e)
    return "";
  const t = e.className.match(/gradio-container-(.+)/);
  return t ? t[1] : "";
}
const kl = +jl()[0];
function nt(e, t, n) {
  const r = kl >= 5 ? "gradio_api/" : "";
  return e == null ? n ? `/proxy=${n}${r}file=` : `${t}${r}file=` : Ol(e) ? e : n ? `/proxy=${n}${r}file=${e}` : `${t}/${r}file=${e}`;
}
const Al = (e) => !!e.url;
function To(e, t, n) {
  if (e)
    return Al(e) ? e.url : typeof e == "string" ? e.startsWith("http") ? e : nt(e, t, n) : e;
}
const zl = ({
  options: e,
  urlProxyUrl: t,
  urlRoot: n,
  onWelcomePromptSelect: r
}) => {
  var a;
  const {
    prompts: o,
    ...s
  } = e, i = fe(() => be(o || {}, {
    omitNull: !0
  }), [o]);
  return /* @__PURE__ */ S.jsxs(Ce, {
    vertical: !0,
    gap: "middle",
    children: [/* @__PURE__ */ S.jsx(cl, {
      ...s,
      icon: To(s.icon, n, t),
      styles: {
        ...s == null ? void 0 : s.styles,
        icon: {
          flexShrink: 0,
          ...(a = s == null ? void 0 : s.styles) == null ? void 0 : a.icon
        }
      },
      classNames: s.class_names,
      className: N(s.elem_classes),
      style: s.elem_style
    }), /* @__PURE__ */ S.jsx(Cn, {
      ...i,
      classNames: i == null ? void 0 : i.class_names,
      className: N(i == null ? void 0 : i.elem_classes),
      style: i == null ? void 0 : i.elem_style,
      onItemClick: ({
        data: l
      }) => {
        r({
          value: l
        });
      }
    })]
  });
}, $r = Symbol(), Rr = Symbol(), Ir = Symbol(), Pr = Symbol(), Dl = (e) => e ? typeof e == "string" ? {
  src: e
} : ((n) => !!n.url)(e) ? {
  src: e.url
} : e.src ? {
  ...e,
  src: typeof e.src == "string" ? e.src : e.src.url
} : e : void 0, Hl = (e) => typeof e == "string" ? [{
  type: "text",
  content: e
}] : Array.isArray(e) ? e.map((t) => typeof t == "string" ? {
  type: "text",
  content: t
} : t) : ve(e) ? [e] : [], Bl = (e, t) => {
  if (typeof e == "string")
    return t[0];
  if (Array.isArray(e)) {
    const n = [...e];
    return Object.keys(t).forEach((r) => {
      const o = n[r];
      typeof o == "string" ? n[r] = t[r] : n[r] = {
        ...o,
        content: t[r]
      };
    }), n;
  }
  return ve(e) ? {
    ...e,
    content: t[0]
  } : e;
}, $o = (e, t, n) => typeof e == "string" ? e : Array.isArray(e) ? e.map((r) => $o(r, t, n)).filter(Boolean).join(`
`) : ve(e) ? e.copyable ?? !0 ? typeof e.content == "string" ? e.content : e.type === "file" ? JSON.stringify(e.content.map((r) => To(r, t, n))) : JSON.stringify(e.content) : "" : JSON.stringify(e), Ro = (e, t) => (e || []).map((n) => ({
  ...t(n),
  children: Array.isArray(n.children) ? Ro(n.children, t) : void 0
})), Wl = ({
  content: e,
  className: t,
  style: n,
  disabled: r,
  urlRoot: o,
  urlProxyUrl: s,
  onCopy: i
}) => {
  const a = fe(() => $o(e, o, s), [e, s, o]), l = J(null);
  return /* @__PURE__ */ S.jsx($e.Text, {
    copyable: {
      tooltips: !1,
      onCopy() {
        i == null || i(a);
      },
      text: a,
      icon: [/* @__PURE__ */ S.jsx(ie, {
        ref: l,
        variant: "text",
        color: "default",
        disabled: r,
        size: "small",
        className: t,
        style: n,
        icon: /* @__PURE__ */ S.jsx(ns, {})
      }, "copy"), /* @__PURE__ */ S.jsx(ie, {
        variant: "text",
        color: "default",
        size: "small",
        disabled: r,
        className: t,
        style: n,
        icon: /* @__PURE__ */ S.jsx(Lr, {})
      }, "copied")]
    }
  });
}, Vl = ({
  action: e,
  disabledActions: t,
  message: n,
  onCopy: r,
  onDelete: o,
  onEdit: s,
  onLike: i,
  onRetry: a,
  urlRoot: l,
  urlProxyUrl: u
}) => {
  var y;
  const m = J(), f = () => ve(e) ? {
    action: e.action,
    disabled: (t == null ? void 0 : t.includes(e.action)) || !!e.disabled,
    disableHandler: !!e.popconfirm
  } : {
    action: e,
    disabled: (t == null ? void 0 : t.includes(e)) || !1,
    disableHandler: !1
  }, {
    action: d,
    disabled: p,
    disableHandler: v
  } = f(), g = (() => {
    var _, C;
    switch (d) {
      case "copy":
        return /* @__PURE__ */ S.jsx(Wl, {
          disabled: p,
          content: n.content,
          onCopy: r,
          urlRoot: l,
          urlProxyUrl: u
        });
      case "like":
        return m.current = () => i(!0), /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: ((_ = n.meta) == null ? void 0 : _.feedback) === "like" ? "primary" : "default",
          disabled: p,
          size: "small",
          icon: /* @__PURE__ */ S.jsx(ts, {}),
          onClick: () => {
            !v && i(!0);
          }
        });
      case "dislike":
        return m.current = () => i(!1), /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: ((C = n.meta) == null ? void 0 : C.feedback) === "dislike" ? "primary" : "default",
          size: "small",
          icon: /* @__PURE__ */ S.jsx(es, {}),
          disabled: p,
          onClick: () => !v && i(!1)
        });
      case "retry":
        return m.current = a, /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ S.jsx(Jo, {}),
          onClick: () => !v && a()
        });
      case "edit":
        return m.current = s, /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ S.jsx(Qo, {}),
          onClick: () => !v && s()
        });
      case "delete":
        return m.current = o, /* @__PURE__ */ S.jsx(ie, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ S.jsx(Zo, {}),
          onClick: () => !v && o()
        });
      default:
        return null;
    }
  })();
  if (ve(e)) {
    const _ = {
      ...typeof e.popconfirm == "string" ? {
        title: e.popconfirm
      } : {
        ...e.popconfirm,
        title: (y = e.popconfirm) == null ? void 0 : y.title
      },
      disabled: p,
      onConfirm() {
        var C;
        (C = m.current) == null || C.call(m);
      }
    };
    return c.createElement(e.popconfirm ? cs : c.Fragment, e.popconfirm ? _ : void 0, c.createElement(e.tooltip ? us : c.Fragment, e.tooltip ? typeof e.tooltip == "string" ? {
      title: e.tooltip
    } : e.tooltip : void 0, g));
  }
  return g;
}, Xl = ({
  isEditing: e,
  onEditCancel: t,
  onEditConfirm: n,
  onCopy: r,
  onEdit: o,
  onLike: s,
  onDelete: i,
  onRetry: a,
  editValues: l,
  message: u,
  extra: m,
  index: f,
  actions: d,
  disabledActions: p,
  urlRoot: v,
  urlProxyUrl: h
}) => e ? /* @__PURE__ */ S.jsxs(Ce, {
  justify: "end",
  children: [/* @__PURE__ */ S.jsx(ie, {
    variant: "text",
    color: "default",
    size: "small",
    icon: /* @__PURE__ */ S.jsx(Yo, {}),
    onClick: () => {
      t == null || t();
    }
  }), /* @__PURE__ */ S.jsx(ie, {
    variant: "text",
    color: "default",
    size: "small",
    icon: /* @__PURE__ */ S.jsx(Lr, {}),
    onClick: () => {
      const g = Bl(u.content, l);
      n == null || n({
        index: f,
        value: g,
        previous_value: u.content
      });
    }
  })]
}) : /* @__PURE__ */ S.jsx(Ce, {
  justify: "space-between",
  align: "center",
  gap: m && (d != null && d.length) ? "small" : void 0,
  children: (u.role === "user" ? ["extra", "actions"] : ["actions", "extra"]).map((g) => {
    switch (g) {
      case "extra":
        return /* @__PURE__ */ S.jsx($e.Text, {
          type: "secondary",
          children: m
        }, "extra");
      case "actions":
        return /* @__PURE__ */ S.jsx("div", {
          children: (d || []).map((y, _) => /* @__PURE__ */ S.jsx(Vl, {
            urlRoot: v,
            urlProxyUrl: h,
            action: y,
            disabledActions: p,
            message: u,
            onCopy: (C) => r({
              value: C,
              index: f
            }),
            onDelete: () => i({
              index: f,
              value: u.content
            }),
            onEdit: () => o(f),
            onLike: (C) => s == null ? void 0 : s({
              value: u.content,
              liked: C,
              index: f
            }),
            onRetry: () => a == null ? void 0 : a({
              index: f,
              value: u.content
            })
          }, `${y}-${_}`))
        }, "actions");
    }
  })
}), Ul = ({
  markdownConfig: e,
  title: t
}) => t ? e.renderMarkdown ? /* @__PURE__ */ S.jsx(vt, {
  ...e,
  value: t
}) : /* @__PURE__ */ S.jsx(S.Fragment, {
  children: t
}) : null, Gl = ({
  item: e,
  urlRoot: t,
  urlProxyUrl: n,
  ...r
}) => {
  const o = fe(() => e ? typeof e == "string" ? {
    url: e.startsWith("http") ? e : nt(e, t, n),
    uid: e,
    name: e.split("/").pop()
  } : {
    ...e,
    uid: e.uid || e.path || e.url,
    name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
    url: e.url || nt(e.path, t, n)
  } : {}, [e, n, t]);
  return /* @__PURE__ */ S.jsx(go.FileCard, {
    ...r,
    imageProps: {
      ...r.imageProps
      // fixed in @ant-design/x@1.2.0
      // wrapperStyle: {
      //   width: '100%',
      //   height: '100%',
      //   ...props.imageProps?.wrapperStyle,
      // },
      // style: {
      //   width: '100%',
      //   height: '100%',
      //   objectFit: 'contain',
      //   borderRadius: token.borderRadius,
      //   ...props.imageProps?.style,
      // },
    },
    item: o
  });
}, ql = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"];
function Kl(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
const Yl = (e, t, n) => e ? typeof e == "string" ? {
  url: e.startsWith("http") ? e : nt(e, t, n),
  uid: e,
  name: e.split("/").pop()
} : {
  ...e,
  uid: e.uid || e.path || e.url,
  name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
  url: e.url || nt(e.path, t, n)
} : {}, Zl = ({
  children: e,
  item: t
}) => {
  const {
    token: n
  } = Qe.useToken(), r = fe(() => {
    const o = t.name || "", s = o.match(/^(.*)\.[^.]+$/), i = s ? o.slice(s[1].length) : "";
    return Kl(i, ql);
  }, [t.name]);
  return /* @__PURE__ */ S.jsx("div", {
    className: "ms-gr-pro-chatbot-message-file-message-container",
    style: {
      borderRadius: n.borderRadius
    },
    children: r ? /* @__PURE__ */ S.jsxs(S.Fragment, {
      children: [" ", e]
    }) : /* @__PURE__ */ S.jsxs(S.Fragment, {
      children: [e, /* @__PURE__ */ S.jsx("div", {
        className: "ms-gr-pro-chatbot-message-file-message-toolbar",
        style: {
          backgroundColor: n.colorBgMask,
          zIndex: n.zIndexPopupBase,
          borderRadius: n.borderRadius
        },
        children: /* @__PURE__ */ S.jsx(ie, {
          icon: /* @__PURE__ */ S.jsx(rs, {
            style: {
              color: n.colorWhite
            }
          }),
          variant: "link",
          color: "default",
          size: "small",
          href: t.url,
          target: "_blank",
          rel: "noopener noreferrer"
        })
      })]
    })
  });
}, Ql = ({
  value: e,
  urlProxyUrl: t,
  urlRoot: n,
  options: r
}) => {
  const {
    imageProps: o
  } = r;
  return /* @__PURE__ */ S.jsx(Ce, {
    gap: "small",
    wrap: !0,
    ...r,
    className: "ms-gr-pro-chatbot-message-file-message",
    children: e == null ? void 0 : e.map((s, i) => {
      const a = Yl(s, n, t);
      return /* @__PURE__ */ S.jsx(Zl, {
        item: a,
        children: /* @__PURE__ */ S.jsx(Gl, {
          item: a,
          urlRoot: n,
          urlProxyUrl: t,
          imageProps: o
        })
      }, `${a.uid}-${i}`);
    })
  });
}, Jl = ({
  value: e,
  options: t,
  onItemClick: n
}) => {
  const {
    elem_style: r,
    elem_classes: o,
    class_names: s,
    styles: i,
    ...a
  } = t;
  return /* @__PURE__ */ S.jsx(Cn, {
    ...a,
    classNames: s,
    className: N(o),
    style: r,
    styles: i,
    items: e,
    onItemClick: ({
      data: l
    }) => {
      n(l);
    }
  });
}, Mr = ({
  value: e,
  options: t
}) => {
  const {
    renderMarkdown: n,
    ...r
  } = t;
  return /* @__PURE__ */ S.jsx(S.Fragment, {
    children: n ? /* @__PURE__ */ S.jsx(vt, {
      ...r,
      value: e
    }) : e
  });
}, ec = ({
  value: e,
  options: t
}) => {
  const {
    renderMarkdown: n,
    status: r,
    title: o,
    ...s
  } = t, [i, a] = Ze(() => r !== "done");
  return Ee(() => {
    a(r !== "done");
  }, [r]), /* @__PURE__ */ S.jsx(S.Fragment, {
    children: /* @__PURE__ */ S.jsx(ds, {
      activeKey: i ? ["tool"] : [],
      onChange: () => {
        a(!i);
      },
      items: [{
        key: "tool",
        label: n ? /* @__PURE__ */ S.jsx(vt, {
          ...s,
          value: o
        }) : o,
        children: n ? /* @__PURE__ */ S.jsx(vt, {
          ...s,
          value: e
        }) : e
      }]
    })
  });
}, tc = ["text", "tool"], nc = ({
  isEditing: e,
  index: t,
  message: n,
  isLastMessage: r,
  markdownConfig: o,
  onEdit: s,
  onSuggestionSelect: i,
  urlProxyUrl: a,
  urlRoot: l
}) => {
  const u = J(null), m = () => Hl(n.content).map((d, p) => {
    const v = () => {
      var h;
      if (e && (d.editable ?? !0) && tc.includes(d.type)) {
        const g = d.content, y = (h = u.current) == null ? void 0 : h.getBoundingClientRect().width;
        return /* @__PURE__ */ S.jsx("div", {
          style: {
            width: y,
            minWidth: 200,
            maxWidth: "100%"
          },
          children: /* @__PURE__ */ S.jsx(fs.TextArea, {
            autoSize: {
              minRows: 1,
              maxRows: 10
            },
            defaultValue: g,
            onChange: (_) => {
              s(p, _.target.value);
            }
          })
        });
      }
      switch (d.type) {
        case "text":
          return /* @__PURE__ */ S.jsx(Mr, {
            value: d.content,
            options: be({
              ...o,
              ...mt(d.options)
            }, {
              omitNull: !0
            })
          });
        case "tool":
          return /* @__PURE__ */ S.jsx(ec, {
            value: d.content,
            options: be({
              ...o,
              ...mt(d.options)
            }, {
              omitNull: !0
            })
          });
        case "file":
          return /* @__PURE__ */ S.jsx(Ql, {
            value: d.content,
            urlRoot: l,
            urlProxyUrl: a,
            options: be(d.options || {}, {
              omitNull: !0
            })
          });
        case "suggestion":
          return /* @__PURE__ */ S.jsx(Jl, {
            value: r ? d.content : Ro(d.content, (g) => ({
              ...g,
              disabled: g.disabled ?? !0
            })),
            options: be(d.options || {}, {
              omitNull: !0
            }),
            onItemClick: (g) => {
              i({
                index: t,
                value: g
              });
            }
          });
        default:
          return typeof d.content != "string" ? null : /* @__PURE__ */ S.jsx(Mr, {
            value: d.content,
            options: be({
              ...o,
              ...mt(d.options)
            }, {
              omitNull: !0
            })
          });
      }
    };
    return /* @__PURE__ */ S.jsx(c.Fragment, {
      children: v()
    }, p);
  });
  return /* @__PURE__ */ S.jsx("div", {
    ref: u,
    children: /* @__PURE__ */ S.jsx(Ce, {
      vertical: !0,
      gap: "small",
      children: m()
    })
  });
}, dc = ti(Sl(["roles"], ({
  id: e,
  className: t,
  style: n,
  height: r,
  minHeight: o,
  maxHeight: s,
  value: i,
  roles: a,
  urlRoot: l,
  urlProxyUrl: u,
  themeMode: m,
  autoScroll: f = !0,
  showScrollToBottomButton: d = !0,
  scrollToBottomButtonOffset: p = 200,
  markdownConfig: v,
  welcomeConfig: h,
  userConfig: g,
  botConfig: y,
  onValueChange: _,
  onCopy: C,
  onChange: T,
  onEdit: $,
  onRetry: x,
  onDelete: I,
  onLike: M,
  onSuggestionSelect: k,
  onWelcomePromptSelect: R
}) => {
  const L = fe(() => ({
    variant: "borderless",
    ...h ? be(h, {
      omitNull: !0
    }) : {}
  }), [h]), F = fe(() => ({
    lineBreaks: !0,
    renderMarkdown: !0,
    ...mt(v),
    urlRoot: l,
    themeMode: m
  }), [v, m, l]), b = fe(() => g ? be(g, {
    omitNull: !0
  }) : {}, [g]), w = fe(() => y ? be(y, {
    omitNull: !0
  }) : {}, [y]), O = fe(() => {
    const E = (i || []).map((q, V) => {
      const pe = V === i.length - 1, de = be(q, {
        omitNull: !0
      });
      return {
        ...An(de, ["header", "footer", "avatar"]),
        [Co]: V,
        [$r]: de.header,
        [Rr]: de.footer,
        [Ir]: de.avatar,
        [Pr]: pe,
        key: de.key ?? `${V}`
      };
    }).filter((q) => q.role !== "system");
    return E.length > 0 ? E : [{
      role: "chatbot-internal-welcome"
    }];
  }, [i]), z = J(null), [D, W] = Ze(-1), [ne, se] = Ze({}), U = J(), B = oe((E, q) => {
    se((V) => ({
      ...V,
      [E]: q
    }));
  }), G = oe(T);
  Ee(() => {
    Is(U.current, i) || (G(), U.current = i);
  }, [i, G]);
  const X = oe((E) => {
    k == null || k(E);
  }), K = oe((E) => {
    R == null || R(E);
  }), ae = oe((E) => {
    x == null || x(E);
  }), re = oe((E) => {
    W(E);
  }), Se = oe(() => {
    W(-1);
  }), je = oe((E) => {
    W(-1), _([...i.slice(0, E.index), {
      ...i[E.index],
      content: E.value
    }, ...i.slice(E.index + 1)]), $ == null || $(E);
  }), ke = oe((E) => {
    C == null || C(E);
  }), Ae = oe((E) => {
    M == null || M(E), _(Cr(i, (q) => {
      const V = q[E.index].meta || {}, pe = E.liked ? "like" : "dislike";
      q[E.index] = {
        ...q[E.index],
        meta: {
          ...V,
          feedback: V.feedback === pe ? null : pe
        }
      };
    }));
  }), we = oe((E) => {
    _(Cr(i, (q) => {
      q.splice(E.index, 1);
    })), I == null || I(E);
  }), ze = Nl({
    roles: a,
    preProcess(E, q) {
      var pe, de, Q, Y, le, Ie, Pe, Rn, In, Pn, Mn, Ln;
      const V = E.role === "user";
      return {
        ...E,
        style: E.elem_style,
        className: N(E.elem_classes, "ms-gr-pro-chatbot-message"),
        classNames: {
          ...E.class_names,
          avatar: N(V ? (pe = b == null ? void 0 : b.class_names) == null ? void 0 : pe.avatar : (de = w == null ? void 0 : w.class_names) == null ? void 0 : de.avatar, (Q = E.class_names) == null ? void 0 : Q.avatar, "ms-gr-pro-chatbot-message-avatar"),
          header: N(V ? (Y = b == null ? void 0 : b.class_names) == null ? void 0 : Y.header : (le = w == null ? void 0 : w.class_names) == null ? void 0 : le.header, (Ie = E.class_names) == null ? void 0 : Ie.header, "ms-gr-pro-chatbot-message-header"),
          footer: N(V ? (Pe = b == null ? void 0 : b.class_names) == null ? void 0 : Pe.footer : (Rn = w == null ? void 0 : w.class_names) == null ? void 0 : Rn.footer, (In = E.class_names) == null ? void 0 : In.footer, "ms-gr-pro-chatbot-message-footer", q === D ? "ms-gr-pro-chatbot-message-footer-editing" : void 0),
          content: N(V ? (Pn = b == null ? void 0 : b.class_names) == null ? void 0 : Pn.content : (Mn = w == null ? void 0 : w.class_names) == null ? void 0 : Mn.content, (Ln = E.class_names) == null ? void 0 : Ln.content, "ms-gr-pro-chatbot-message-content")
        }
      };
    },
    postProcess(E, q) {
      const V = E.role === "user";
      switch (E.role) {
        case "chatbot-internal-welcome":
          return {
            variant: "borderless",
            styles: {
              content: {
                width: "100%"
              }
            },
            messageRender() {
              return /* @__PURE__ */ S.jsx(zl, {
                urlRoot: l,
                urlProxyUrl: u,
                options: L || {},
                onWelcomePromptSelect: K
              });
            }
          };
        case "user":
        case "assistant":
          return {
            ...An(V ? b : w, ["actions", "avatar", "header"]),
            ...E,
            style: {
              ...V ? b == null ? void 0 : b.style : w == null ? void 0 : w.style,
              ...E.style
            },
            className: N(E.className, V ? b == null ? void 0 : b.elem_classes : w == null ? void 0 : w.elem_classes),
            header: /* @__PURE__ */ S.jsx(Ul, {
              title: E[$r] ?? (V ? b == null ? void 0 : b.header : w == null ? void 0 : w.header),
              markdownConfig: F
            }),
            avatar: Dl(E[Ir] ?? (V ? b == null ? void 0 : b.avatar : w == null ? void 0 : w.avatar)),
            footer: (
              // bubbleProps[lastMessageSymbol] &&
              E.loading || E.status === "pending" ? null : /* @__PURE__ */ S.jsx(Xl, {
                isEditing: D === q,
                message: E,
                extra: E[Rr] ?? (V ? b == null ? void 0 : b.footer : w == null ? void 0 : w.footer),
                urlRoot: l,
                urlProxyUrl: u,
                editValues: ne,
                index: q,
                actions: E.actions ?? (V ? (b == null ? void 0 : b.actions) || [] : (w == null ? void 0 : w.actions) || []),
                disabledActions: E.disabled_actions ?? (V ? (b == null ? void 0 : b.disabled_actions) || [] : (w == null ? void 0 : w.disabled_actions) || []),
                onEditCancel: Se,
                onEditConfirm: je,
                onCopy: ke,
                onEdit: re,
                onDelete: we,
                onRetry: ae,
                onLike: Ae
              })
            ),
            messageRender() {
              return /* @__PURE__ */ S.jsx(nc, {
                index: q,
                urlProxyUrl: u,
                urlRoot: l,
                isEditing: D === q,
                message: E,
                isLastMessage: E[Pr] || !1,
                markdownConfig: F,
                onEdit: B,
                onSuggestionSelect: X
              });
            }
          };
        default:
          return;
      }
    }
  }, [D, b, L, w, F, ne]), {
    scrollToBottom: ot,
    showScrollButton: Bt
  } = Fl({
    ref: z,
    value: i,
    autoScroll: f,
    scrollButtonOffset: p
  });
  return /* @__PURE__ */ S.jsxs("div", {
    id: e,
    className: N(t, "ms-gr-pro-chatbot"),
    style: {
      height: r,
      minHeight: o,
      maxHeight: s,
      ...n
    },
    children: [/* @__PURE__ */ S.jsx(En.List, {
      ref: z,
      className: "ms-gr-pro-chatbot-messages",
      autoScroll: !1,
      roles: ze,
      items: O
    }), d && Bt && /* @__PURE__ */ S.jsx("div", {
      className: "ms-gr-pro-chatbot-scroll-to-bottom-button",
      children: /* @__PURE__ */ S.jsx(ie, {
        icon: /* @__PURE__ */ S.jsx(os, {}),
        shape: "circle",
        variant: "outlined",
        color: "primary",
        onClick: () => ot("smooth")
      })
    })]
  });
}));
export {
  dc as Chatbot,
  dc as default
};
