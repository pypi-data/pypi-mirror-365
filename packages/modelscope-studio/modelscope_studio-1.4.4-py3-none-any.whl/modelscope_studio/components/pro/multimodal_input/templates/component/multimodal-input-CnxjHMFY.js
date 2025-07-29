import { i as Qr, a as Gt, r as Jr, b as ei, Z as it, g as ti, c as Z, d as ni, e as ri, o as ii } from "./Index-CvVzdF6C.js";
const R = window.ms_globals.React, f = window.ms_globals.React, Ur = window.ms_globals.React.forwardRef, pe = window.ms_globals.React.useRef, $e = window.ms_globals.React.useState, Ce = window.ms_globals.React.useEffect, Xr = window.ms_globals.React.version, Gr = window.ms_globals.React.isValidElement, qr = window.ms_globals.React.useLayoutEffect, Kr = window.ms_globals.React.useImperativeHandle, Yr = window.ms_globals.React.memo, Xt = window.ms_globals.React.useMemo, Zr = window.ms_globals.React.useCallback, pn = window.ms_globals.ReactDOM, ut = window.ms_globals.ReactDOM.createPortal, oi = window.ms_globals.internalContext.useContextPropsContext, si = window.ms_globals.internalContext.useSuggestionOpenContext, ai = window.ms_globals.antdIcons.FileTextFilled, li = window.ms_globals.antdIcons.CloseCircleFilled, ci = window.ms_globals.antdIcons.FileExcelFilled, ui = window.ms_globals.antdIcons.FileImageFilled, di = window.ms_globals.antdIcons.FileMarkdownFilled, fi = window.ms_globals.antdIcons.FilePdfFilled, hi = window.ms_globals.antdIcons.FilePptFilled, pi = window.ms_globals.antdIcons.FileWordFilled, mi = window.ms_globals.antdIcons.FileZipFilled, gi = window.ms_globals.antdIcons.PlusOutlined, vi = window.ms_globals.antdIcons.LeftOutlined, bi = window.ms_globals.antdIcons.RightOutlined, yi = window.ms_globals.antdIcons.CloseOutlined, wi = window.ms_globals.antdIcons.ClearOutlined, Si = window.ms_globals.antdIcons.ArrowUpOutlined, xi = window.ms_globals.antdIcons.AudioMutedOutlined, Ci = window.ms_globals.antdIcons.AudioOutlined, Ei = window.ms_globals.antdIcons.LinkOutlined, _i = window.ms_globals.antdIcons.CloudUploadOutlined, Ri = window.ms_globals.antd.ConfigProvider, dt = window.ms_globals.antd.theme, rr = window.ms_globals.antd.Upload, Ti = window.ms_globals.antd.Progress, Pi = window.ms_globals.antd.Image, De = window.ms_globals.antd.Button, ft = window.ms_globals.antd.Flex, At = window.ms_globals.antd.Typography, Mi = window.ms_globals.antd.Input, Li = window.ms_globals.antd.Tooltip, Oi = window.ms_globals.antd.Badge, qt = window.ms_globals.antdCssinjs.unit, $t = window.ms_globals.antdCssinjs.token2CSSVar, mn = window.ms_globals.antdCssinjs.useStyleRegister, Ai = window.ms_globals.antdCssinjs.useCSSVarRegister, $i = window.ms_globals.antdCssinjs.createTheme, Di = window.ms_globals.antdCssinjs.useCacheToken;
var ki = /\s/;
function Ii(n) {
  for (var e = n.length; e-- && ki.test(n.charAt(e)); )
    ;
  return e;
}
var Ni = /^\s+/;
function Wi(n) {
  return n && n.slice(0, Ii(n) + 1).replace(Ni, "");
}
var gn = NaN, Fi = /^[-+]0x[0-9a-f]+$/i, ji = /^0b[01]+$/i, Bi = /^0o[0-7]+$/i, Hi = parseInt;
function vn(n) {
  if (typeof n == "number")
    return n;
  if (Qr(n))
    return gn;
  if (Gt(n)) {
    var e = typeof n.valueOf == "function" ? n.valueOf() : n;
    n = Gt(e) ? e + "" : e;
  }
  if (typeof n != "string")
    return n === 0 ? n : +n;
  n = Wi(n);
  var t = ji.test(n);
  return t || Bi.test(n) ? Hi(n.slice(2), t ? 2 : 8) : Fi.test(n) ? gn : +n;
}
function zi() {
}
var Dt = function() {
  return Jr.Date.now();
}, Vi = "Expected a function", Ui = Math.max, Xi = Math.min;
function Gi(n, e, t) {
  var r, i, o, s, a, c, l = 0, u = !1, d = !1, h = !0;
  if (typeof n != "function")
    throw new TypeError(Vi);
  e = vn(e) || 0, Gt(t) && (u = !!t.leading, d = "maxWait" in t, o = d ? Ui(vn(t.maxWait) || 0, e) : o, h = "trailing" in t ? !!t.trailing : h);
  function p(w) {
    var _ = r, P = i;
    return r = i = void 0, l = w, s = n.apply(P, _), s;
  }
  function v(w) {
    return l = w, a = setTimeout(m, e), u ? p(w) : s;
  }
  function b(w) {
    var _ = w - c, P = w - l, O = e - _;
    return d ? Xi(O, o - P) : O;
  }
  function g(w) {
    var _ = w - c, P = w - l;
    return c === void 0 || _ >= e || _ < 0 || d && P >= o;
  }
  function m() {
    var w = Dt();
    if (g(w))
      return S(w);
    a = setTimeout(m, b(w));
  }
  function S(w) {
    return a = void 0, h && r ? p(w) : (r = i = void 0, s);
  }
  function C() {
    a !== void 0 && clearTimeout(a), l = 0, r = c = i = a = void 0;
  }
  function y() {
    return a === void 0 ? s : S(Dt());
  }
  function x() {
    var w = Dt(), _ = g(w);
    if (r = arguments, i = this, c = w, _) {
      if (a === void 0)
        return v(c);
      if (d)
        return clearTimeout(a), a = setTimeout(m, e), p(c);
    }
    return a === void 0 && (a = setTimeout(m, e)), s;
  }
  return x.cancel = C, x.flush = y, x;
}
function qi(n, e) {
  return ei(n, e);
}
var ir = {
  exports: {}
}, mt = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ki = f, Yi = Symbol.for("react.element"), Zi = Symbol.for("react.fragment"), Qi = Object.prototype.hasOwnProperty, Ji = Ki.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, eo = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function or(n, e, t) {
  var r, i = {}, o = null, s = null;
  t !== void 0 && (o = "" + t), e.key !== void 0 && (o = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (r in e) Qi.call(e, r) && !eo.hasOwnProperty(r) && (i[r] = e[r]);
  if (n && n.defaultProps) for (r in e = n.defaultProps, e) i[r] === void 0 && (i[r] = e[r]);
  return {
    $$typeof: Yi,
    type: n,
    key: o,
    ref: s,
    props: i,
    _owner: Ji.current
  };
}
mt.Fragment = Zi;
mt.jsx = or;
mt.jsxs = or;
ir.exports = mt;
var q = ir.exports;
const {
  SvelteComponent: to,
  assign: bn,
  binding_callbacks: yn,
  check_outros: no,
  children: sr,
  claim_element: ar,
  claim_space: ro,
  component_subscribe: wn,
  compute_slots: io,
  create_slot: oo,
  detach: Le,
  element: lr,
  empty: Sn,
  exclude_internal_props: xn,
  get_all_dirty_from_scope: so,
  get_slot_changes: ao,
  group_outros: lo,
  init: co,
  insert_hydration: ot,
  safe_not_equal: uo,
  set_custom_element_data: cr,
  space: fo,
  transition_in: st,
  transition_out: Kt,
  update_slot_base: ho
} = window.__gradio__svelte__internal, {
  beforeUpdate: po,
  getContext: mo,
  onDestroy: go,
  setContext: vo
} = window.__gradio__svelte__internal;
function Cn(n) {
  let e, t;
  const r = (
    /*#slots*/
    n[7].default
  ), i = oo(
    r,
    n,
    /*$$scope*/
    n[6],
    null
  );
  return {
    c() {
      e = lr("svelte-slot"), i && i.c(), this.h();
    },
    l(o) {
      e = ar(o, "SVELTE-SLOT", {
        class: !0
      });
      var s = sr(e);
      i && i.l(s), s.forEach(Le), this.h();
    },
    h() {
      cr(e, "class", "svelte-1rt0kpf");
    },
    m(o, s) {
      ot(o, e, s), i && i.m(e, null), n[9](e), t = !0;
    },
    p(o, s) {
      i && i.p && (!t || s & /*$$scope*/
      64) && ho(
        i,
        r,
        o,
        /*$$scope*/
        o[6],
        t ? ao(
          r,
          /*$$scope*/
          o[6],
          s,
          null
        ) : so(
          /*$$scope*/
          o[6]
        ),
        null
      );
    },
    i(o) {
      t || (st(i, o), t = !0);
    },
    o(o) {
      Kt(i, o), t = !1;
    },
    d(o) {
      o && Le(e), i && i.d(o), n[9](null);
    }
  };
}
function bo(n) {
  let e, t, r, i, o = (
    /*$$slots*/
    n[4].default && Cn(n)
  );
  return {
    c() {
      e = lr("react-portal-target"), t = fo(), o && o.c(), r = Sn(), this.h();
    },
    l(s) {
      e = ar(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), sr(e).forEach(Le), t = ro(s), o && o.l(s), r = Sn(), this.h();
    },
    h() {
      cr(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      ot(s, e, a), n[8](e), ot(s, t, a), o && o.m(s, a), ot(s, r, a), i = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? o ? (o.p(s, a), a & /*$$slots*/
      16 && st(o, 1)) : (o = Cn(s), o.c(), st(o, 1), o.m(r.parentNode, r)) : o && (lo(), Kt(o, 1, 1, () => {
        o = null;
      }), no());
    },
    i(s) {
      i || (st(o), i = !0);
    },
    o(s) {
      Kt(o), i = !1;
    },
    d(s) {
      s && (Le(e), Le(t), Le(r)), n[8](null), o && o.d(s);
    }
  };
}
function En(n) {
  const {
    svelteInit: e,
    ...t
  } = n;
  return t;
}
function yo(n, e, t) {
  let r, i, {
    $$slots: o = {},
    $$scope: s
  } = e;
  const a = io(o);
  let {
    svelteInit: c
  } = e;
  const l = it(En(e)), u = it();
  wn(n, u, (y) => t(0, r = y));
  const d = it();
  wn(n, d, (y) => t(1, i = y));
  const h = [], p = mo("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: b,
    subSlotIndex: g
  } = ti() || {}, m = c({
    parent: p,
    props: l,
    target: u,
    slot: d,
    slotKey: v,
    slotIndex: b,
    subSlotIndex: g,
    onDestroy(y) {
      h.push(y);
    }
  });
  vo("$$ms-gr-react-wrapper", m), po(() => {
    l.set(En(e));
  }), go(() => {
    h.forEach((y) => y());
  });
  function S(y) {
    yn[y ? "unshift" : "push"](() => {
      r = y, u.set(r);
    });
  }
  function C(y) {
    yn[y ? "unshift" : "push"](() => {
      i = y, d.set(i);
    });
  }
  return n.$$set = (y) => {
    t(17, e = bn(bn({}, e), xn(y))), "svelteInit" in y && t(5, c = y.svelteInit), "$$scope" in y && t(6, s = y.$$scope);
  }, e = xn(e), [r, i, u, d, a, c, s, o, S, C];
}
class wo extends to {
  constructor(e) {
    super(), co(this, e, yo, bo, uo, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Za
} = window.__gradio__svelte__internal, _n = window.ms_globals.rerender, kt = window.ms_globals.tree;
function So(n, e = {}) {
  function t(r) {
    const i = it(), o = new wo({
      ...r,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: n,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: e.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? kt;
          return c.nodes = [...c.nodes, a], _n({
            createPortal: ut,
            node: kt
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== i), _n({
              createPortal: ut,
              node: kt
            });
          }), a;
        },
        ...r.props
      }
    });
    return i.set(o), o;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise.then(() => {
      r(t);
    });
  });
}
const xo = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Co(n) {
  return n ? Object.keys(n).reduce((e, t) => {
    const r = n[t];
    return e[t] = Eo(t, r), e;
  }, {}) : {};
}
function Eo(n, e) {
  return typeof e == "number" && !xo.includes(n) ? e + "px" : e;
}
function Yt(n) {
  const e = [], t = n.cloneNode(!1);
  if (n._reactElement) {
    const i = f.Children.toArray(n._reactElement.props.children).map((o) => {
      if (f.isValidElement(o) && o.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Yt(o.props.el);
        return f.cloneElement(o, {
          ...o.props,
          el: a,
          children: [...f.Children.toArray(o.props.children), ...s]
        });
      }
      return null;
    });
    return i.originalChildren = n._reactElement.props.children, e.push(ut(f.cloneElement(n._reactElement, {
      ...n._reactElement.props,
      children: i
    }), t)), {
      clonedElement: t,
      portals: e
    };
  }
  Object.keys(n.getEventListeners()).forEach((i) => {
    n.getEventListeners(i).forEach(({
      listener: s,
      type: a,
      useCapture: c
    }) => {
      t.addEventListener(a, s, c);
    });
  });
  const r = Array.from(n.childNodes);
  for (let i = 0; i < r.length; i++) {
    const o = r[i];
    if (o.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Yt(o);
      e.push(...a), t.appendChild(s);
    } else o.nodeType === 3 && t.appendChild(o.cloneNode());
  }
  return {
    clonedElement: t,
    portals: e
  };
}
function _o(n, e) {
  n && (typeof n == "function" ? n(e) : n.current = e);
}
const Fe = Ur(({
  slot: n,
  clone: e,
  className: t,
  style: r,
  observeAttributes: i
}, o) => {
  const s = pe(), [a, c] = $e([]), {
    forceClone: l
  } = oi(), u = l ? !0 : e;
  return Ce(() => {
    var b;
    if (!s.current || !n)
      return;
    let d = n;
    function h() {
      let g = d;
      if (d.tagName.toLowerCase() === "svelte-slot" && d.children.length === 1 && d.children[0] && (g = d.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), _o(o, g), t && g.classList.add(...t.split(" ")), r) {
        const m = Co(r);
        Object.keys(m).forEach((S) => {
          g.style[S] = m[S];
        });
      }
    }
    let p = null, v = null;
    if (u && window.MutationObserver) {
      let g = function() {
        var y, x, w;
        (y = s.current) != null && y.contains(d) && ((x = s.current) == null || x.removeChild(d));
        const {
          portals: S,
          clonedElement: C
        } = Yt(n);
        d = C, c(S), d.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          h();
        }, 50), (w = s.current) == null || w.appendChild(d);
      };
      g();
      const m = Gi(() => {
        g(), p == null || p.disconnect(), p == null || p.observe(n, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      p = new window.MutationObserver(m), p.observe(n, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      d.style.display = "contents", h(), (b = s.current) == null || b.appendChild(d);
    return () => {
      var g, m;
      d.style.display = "", (g = s.current) != null && g.contains(d) && ((m = s.current) == null || m.removeChild(d)), p == null || p.disconnect();
    };
  }, [n, u, t, r, o, i, l]), f.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Ro = "1.5.0";
function ve() {
  return ve = Object.assign ? Object.assign.bind() : function(n) {
    for (var e = 1; e < arguments.length; e++) {
      var t = arguments[e];
      for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]);
    }
    return n;
  }, ve.apply(null, arguments);
}
function le(n) {
  "@babel/helpers - typeof";
  return le = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, le(n);
}
function To(n, e) {
  if (le(n) != "object" || !n) return n;
  var t = n[Symbol.toPrimitive];
  if (t !== void 0) {
    var r = t.call(n, e);
    if (le(r) != "object") return r;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(n);
}
function ur(n) {
  var e = To(n, "string");
  return le(e) == "symbol" ? e : e + "";
}
function k(n, e, t) {
  return (e = ur(e)) in n ? Object.defineProperty(n, e, {
    value: t,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : n[e] = t, n;
}
function Rn(n, e) {
  var t = Object.keys(n);
  if (Object.getOwnPropertySymbols) {
    var r = Object.getOwnPropertySymbols(n);
    e && (r = r.filter(function(i) {
      return Object.getOwnPropertyDescriptor(n, i).enumerable;
    })), t.push.apply(t, r);
  }
  return t;
}
function D(n) {
  for (var e = 1; e < arguments.length; e++) {
    var t = arguments[e] != null ? arguments[e] : {};
    e % 2 ? Rn(Object(t), !0).forEach(function(r) {
      k(n, r, t[r]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(n, Object.getOwnPropertyDescriptors(t)) : Rn(Object(t)).forEach(function(r) {
      Object.defineProperty(n, r, Object.getOwnPropertyDescriptor(t, r));
    });
  }
  return n;
}
var Po = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, Mo = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Lo = "".concat(Po, " ").concat(Mo).split(/[\s\n]+/), Oo = "aria-", Ao = "data-";
function Tn(n, e) {
  return n.indexOf(e) === 0;
}
function $o(n) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, t;
  e === !1 ? t = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? t = {
    aria: !0
  } : t = D({}, e);
  var r = {};
  return Object.keys(n).forEach(function(i) {
    // Aria
    (t.aria && (i === "role" || Tn(i, Oo)) || // Data
    t.data && Tn(i, Ao) || // Attr
    t.attr && Lo.includes(i)) && (r[i] = n[i]);
  }), r;
}
const Do = /* @__PURE__ */ f.createContext({}), ko = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, dr = (n) => {
  const e = f.useContext(Do);
  return f.useMemo(() => ({
    ...ko,
    ...e[n]
  }), [e[n]]);
};
function Ve() {
  const {
    getPrefixCls: n,
    direction: e,
    csp: t,
    iconPrefixCls: r,
    theme: i
  } = f.useContext(Ri.ConfigContext);
  return {
    theme: i,
    getPrefixCls: n,
    direction: e,
    csp: t,
    iconPrefixCls: r
  };
}
function Io(n) {
  if (Array.isArray(n)) return n;
}
function No(n, e) {
  var t = n == null ? null : typeof Symbol < "u" && n[Symbol.iterator] || n["@@iterator"];
  if (t != null) {
    var r, i, o, s, a = [], c = !0, l = !1;
    try {
      if (o = (t = t.call(n)).next, e === 0) {
        if (Object(t) !== t) return;
        c = !1;
      } else for (; !(c = (r = o.call(t)).done) && (a.push(r.value), a.length !== e); c = !0) ;
    } catch (u) {
      l = !0, i = u;
    } finally {
      try {
        if (!c && t.return != null && (s = t.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw i;
      }
    }
    return a;
  }
}
function Pn(n, e) {
  (e == null || e > n.length) && (e = n.length);
  for (var t = 0, r = Array(e); t < e; t++) r[t] = n[t];
  return r;
}
function Wo(n, e) {
  if (n) {
    if (typeof n == "string") return Pn(n, e);
    var t = {}.toString.call(n).slice(8, -1);
    return t === "Object" && n.constructor && (t = n.constructor.name), t === "Map" || t === "Set" ? Array.from(n) : t === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? Pn(n, e) : void 0;
  }
}
function Fo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function fe(n, e) {
  return Io(n) || No(n, e) || Wo(n, e) || Fo();
}
function Ie(n, e) {
  if (!(n instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function Mn(n, e) {
  for (var t = 0; t < e.length; t++) {
    var r = e[t];
    r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(n, ur(r.key), r);
  }
}
function Ne(n, e, t) {
  return e && Mn(n.prototype, e), t && Mn(n, t), Object.defineProperty(n, "prototype", {
    writable: !1
  }), n;
}
function Te(n) {
  if (n === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return n;
}
function Zt(n, e) {
  return Zt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(t, r) {
    return t.__proto__ = r, t;
  }, Zt(n, e);
}
function gt(n, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  n.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: n,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(n, "prototype", {
    writable: !1
  }), e && Zt(n, e);
}
function ht(n) {
  return ht = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, ht(n);
}
function fr() {
  try {
    var n = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (fr = function() {
    return !!n;
  })();
}
function jo(n, e) {
  if (e && (le(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Te(n);
}
function vt(n) {
  var e = fr();
  return function() {
    var t, r = ht(n);
    if (e) {
      var i = ht(this).constructor;
      t = Reflect.construct(r, arguments, i);
    } else t = r.apply(this, arguments);
    return jo(this, t);
  };
}
var hr = /* @__PURE__ */ Ne(function n() {
  Ie(this, n);
}), pr = "CALC_UNIT", Bo = new RegExp(pr, "g");
function It(n) {
  return typeof n == "number" ? "".concat(n).concat(pr) : n;
}
var Ho = /* @__PURE__ */ function(n) {
  gt(t, n);
  var e = vt(t);
  function t(r, i) {
    var o;
    Ie(this, t), o = e.call(this), k(Te(o), "result", ""), k(Te(o), "unitlessCssVar", void 0), k(Te(o), "lowPriority", void 0);
    var s = le(r);
    return o.unitlessCssVar = i, r instanceof t ? o.result = "(".concat(r.result, ")") : s === "number" ? o.result = It(r) : s === "string" && (o.result = r), o;
  }
  return Ne(t, [{
    key: "add",
    value: function(i) {
      return i instanceof t ? this.result = "".concat(this.result, " + ").concat(i.getResult()) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " + ").concat(It(i))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(i) {
      return i instanceof t ? this.result = "".concat(this.result, " - ").concat(i.getResult()) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " - ").concat(It(i))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(i) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), i instanceof t ? this.result = "".concat(this.result, " * ").concat(i.getResult(!0)) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " * ").concat(i)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(i) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), i instanceof t ? this.result = "".concat(this.result, " / ").concat(i.getResult(!0)) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " / ").concat(i)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(i) {
      return this.lowPriority || i ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(i) {
      var o = this, s = i || {}, a = s.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(l) {
        return o.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(Bo, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), t;
}(hr), zo = /* @__PURE__ */ function(n) {
  gt(t, n);
  var e = vt(t);
  function t(r) {
    var i;
    return Ie(this, t), i = e.call(this), k(Te(i), "result", 0), r instanceof t ? i.result = r.result : typeof r == "number" && (i.result = r), i;
  }
  return Ne(t, [{
    key: "add",
    value: function(i) {
      return i instanceof t ? this.result += i.result : typeof i == "number" && (this.result += i), this;
    }
  }, {
    key: "sub",
    value: function(i) {
      return i instanceof t ? this.result -= i.result : typeof i == "number" && (this.result -= i), this;
    }
  }, {
    key: "mul",
    value: function(i) {
      return i instanceof t ? this.result *= i.result : typeof i == "number" && (this.result *= i), this;
    }
  }, {
    key: "div",
    value: function(i) {
      return i instanceof t ? this.result /= i.result : typeof i == "number" && (this.result /= i), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), t;
}(hr), Vo = function(e, t) {
  var r = e === "css" ? Ho : zo;
  return function(i) {
    return new r(i, t);
  };
}, Ln = function(e, t) {
  return "".concat([t, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function _e(n) {
  var e = R.useRef();
  e.current = n;
  var t = R.useCallback(function() {
    for (var r, i = arguments.length, o = new Array(i), s = 0; s < i; s++)
      o[s] = arguments[s];
    return (r = e.current) === null || r === void 0 ? void 0 : r.call.apply(r, [e].concat(o));
  }, []);
  return t;
}
function bt() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var On = bt() ? R.useLayoutEffect : R.useEffect, Uo = function(e, t) {
  var r = R.useRef(!0);
  On(function() {
    return e(r.current);
  }, t), On(function() {
    return r.current = !1, function() {
      r.current = !0;
    };
  }, []);
}, An = function(e, t) {
  Uo(function(r) {
    if (!r)
      return e();
  }, t);
};
function Ue(n) {
  var e = R.useRef(!1), t = R.useState(n), r = fe(t, 2), i = r[0], o = r[1];
  R.useEffect(function() {
    return e.current = !1, function() {
      e.current = !0;
    };
  }, []);
  function s(a, c) {
    c && e.current || o(a);
  }
  return [i, s];
}
function Nt(n) {
  return n !== void 0;
}
function ln(n, e) {
  var t = e || {}, r = t.defaultValue, i = t.value, o = t.onChange, s = t.postState, a = Ue(function() {
    return Nt(i) ? i : Nt(r) ? typeof r == "function" ? r() : r : typeof n == "function" ? n() : n;
  }), c = fe(a, 2), l = c[0], u = c[1], d = i !== void 0 ? i : l, h = s ? s(d) : d, p = _e(o), v = Ue([d]), b = fe(v, 2), g = b[0], m = b[1];
  An(function() {
    var C = g[0];
    l !== C && p(l, C);
  }, [g]), An(function() {
    Nt(i) || u(i);
  }, [i]);
  var S = _e(function(C, y) {
    u(C, y), m([d], y);
  });
  return [h, S];
}
var mr = {
  exports: {}
}, V = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var cn = Symbol.for("react.element"), un = Symbol.for("react.portal"), yt = Symbol.for("react.fragment"), wt = Symbol.for("react.strict_mode"), St = Symbol.for("react.profiler"), xt = Symbol.for("react.provider"), Ct = Symbol.for("react.context"), Xo = Symbol.for("react.server_context"), Et = Symbol.for("react.forward_ref"), _t = Symbol.for("react.suspense"), Rt = Symbol.for("react.suspense_list"), Tt = Symbol.for("react.memo"), Pt = Symbol.for("react.lazy"), Go = Symbol.for("react.offscreen"), gr;
gr = Symbol.for("react.module.reference");
function be(n) {
  if (typeof n == "object" && n !== null) {
    var e = n.$$typeof;
    switch (e) {
      case cn:
        switch (n = n.type, n) {
          case yt:
          case St:
          case wt:
          case _t:
          case Rt:
            return n;
          default:
            switch (n = n && n.$$typeof, n) {
              case Xo:
              case Ct:
              case Et:
              case Pt:
              case Tt:
              case xt:
                return n;
              default:
                return e;
            }
        }
      case un:
        return e;
    }
  }
}
V.ContextConsumer = Ct;
V.ContextProvider = xt;
V.Element = cn;
V.ForwardRef = Et;
V.Fragment = yt;
V.Lazy = Pt;
V.Memo = Tt;
V.Portal = un;
V.Profiler = St;
V.StrictMode = wt;
V.Suspense = _t;
V.SuspenseList = Rt;
V.isAsyncMode = function() {
  return !1;
};
V.isConcurrentMode = function() {
  return !1;
};
V.isContextConsumer = function(n) {
  return be(n) === Ct;
};
V.isContextProvider = function(n) {
  return be(n) === xt;
};
V.isElement = function(n) {
  return typeof n == "object" && n !== null && n.$$typeof === cn;
};
V.isForwardRef = function(n) {
  return be(n) === Et;
};
V.isFragment = function(n) {
  return be(n) === yt;
};
V.isLazy = function(n) {
  return be(n) === Pt;
};
V.isMemo = function(n) {
  return be(n) === Tt;
};
V.isPortal = function(n) {
  return be(n) === un;
};
V.isProfiler = function(n) {
  return be(n) === St;
};
V.isStrictMode = function(n) {
  return be(n) === wt;
};
V.isSuspense = function(n) {
  return be(n) === _t;
};
V.isSuspenseList = function(n) {
  return be(n) === Rt;
};
V.isValidElementType = function(n) {
  return typeof n == "string" || typeof n == "function" || n === yt || n === St || n === wt || n === _t || n === Rt || n === Go || typeof n == "object" && n !== null && (n.$$typeof === Pt || n.$$typeof === Tt || n.$$typeof === xt || n.$$typeof === Ct || n.$$typeof === Et || n.$$typeof === gr || n.getModuleId !== void 0);
};
V.typeOf = be;
mr.exports = V;
var Wt = mr.exports, qo = Symbol.for("react.element"), Ko = Symbol.for("react.transitional.element"), Yo = Symbol.for("react.fragment");
function Zo(n) {
  return (
    // Base object type
    n && le(n) === "object" && // React Element type
    (n.$$typeof === qo || n.$$typeof === Ko) && // React Fragment type
    n.type === Yo
  );
}
var Qo = Number(Xr.split(".")[0]), Jo = function(e, t) {
  typeof e == "function" ? e(t) : le(e) === "object" && e && "current" in e && (e.current = t);
}, es = function(e) {
  var t, r;
  if (!e)
    return !1;
  if (vr(e) && Qo >= 19)
    return !0;
  var i = Wt.isMemo(e) ? e.type.type : e.type;
  return !(typeof i == "function" && !((t = i.prototype) !== null && t !== void 0 && t.render) && i.$$typeof !== Wt.ForwardRef || typeof e == "function" && !((r = e.prototype) !== null && r !== void 0 && r.render) && e.$$typeof !== Wt.ForwardRef);
};
function vr(n) {
  return /* @__PURE__ */ Gr(n) && !Zo(n);
}
var ts = function(e) {
  if (e && vr(e)) {
    var t = e;
    return t.props.propertyIsEnumerable("ref") ? t.props.ref : t.ref;
  }
  return null;
};
function ns(n, e) {
  for (var t = n, r = 0; r < e.length; r += 1) {
    if (t == null)
      return;
    t = t[e[r]];
  }
  return t;
}
function $n(n, e, t, r) {
  var i = D({}, e[n]);
  if (r != null && r.deprecatedTokens) {
    var o = r.deprecatedTokens;
    o.forEach(function(a) {
      var c = fe(a, 2), l = c[0], u = c[1];
      if (i != null && i[l] || i != null && i[u]) {
        var d;
        (d = i[u]) !== null && d !== void 0 || (i[u] = i == null ? void 0 : i[l]);
      }
    });
  }
  var s = D(D({}, t), i);
  return Object.keys(s).forEach(function(a) {
    s[a] === e[a] && delete s[a];
  }), s;
}
var br = typeof CSSINJS_STATISTIC < "u", Qt = !0;
function Mt() {
  for (var n = arguments.length, e = new Array(n), t = 0; t < n; t++)
    e[t] = arguments[t];
  if (!br)
    return Object.assign.apply(Object, [{}].concat(e));
  Qt = !1;
  var r = {};
  return e.forEach(function(i) {
    if (le(i) === "object") {
      var o = Object.keys(i);
      o.forEach(function(s) {
        Object.defineProperty(r, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return i[s];
          }
        });
      });
    }
  }), Qt = !0, r;
}
var Dn = {};
function rs() {
}
var is = function(e) {
  var t, r = e, i = rs;
  return br && typeof Proxy < "u" && (t = /* @__PURE__ */ new Set(), r = new Proxy(e, {
    get: function(s, a) {
      if (Qt) {
        var c;
        (c = t) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), i = function(s, a) {
    var c;
    Dn[s] = {
      global: Array.from(t),
      component: D(D({}, (c = Dn[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: r,
    keys: t,
    flush: i
  };
};
function kn(n, e, t) {
  if (typeof t == "function") {
    var r;
    return t(Mt(e, (r = e[n]) !== null && r !== void 0 ? r : {}));
  }
  return t ?? {};
}
function os(n) {
  return n === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var t = arguments.length, r = new Array(t), i = 0; i < t; i++)
        r[i] = arguments[i];
      return "max(".concat(r.map(function(o) {
        return qt(o);
      }).join(","), ")");
    },
    min: function() {
      for (var t = arguments.length, r = new Array(t), i = 0; i < t; i++)
        r[i] = arguments[i];
      return "min(".concat(r.map(function(o) {
        return qt(o);
      }).join(","), ")");
    }
  };
}
var ss = 1e3 * 60 * 10, as = /* @__PURE__ */ function() {
  function n() {
    Ie(this, n), k(this, "map", /* @__PURE__ */ new Map()), k(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), k(this, "nextID", 0), k(this, "lastAccessBeat", /* @__PURE__ */ new Map()), k(this, "accessBeat", 0);
  }
  return Ne(n, [{
    key: "set",
    value: function(t, r) {
      this.clear();
      var i = this.getCompositeKey(t);
      this.map.set(i, r), this.lastAccessBeat.set(i, Date.now());
    }
  }, {
    key: "get",
    value: function(t) {
      var r = this.getCompositeKey(t), i = this.map.get(r);
      return this.lastAccessBeat.set(r, Date.now()), this.accessBeat += 1, i;
    }
  }, {
    key: "getCompositeKey",
    value: function(t) {
      var r = this, i = t.map(function(o) {
        return o && le(o) === "object" ? "obj_".concat(r.getObjectID(o)) : "".concat(le(o), "_").concat(o);
      });
      return i.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(t) {
      if (this.objectIDMap.has(t))
        return this.objectIDMap.get(t);
      var r = this.nextID;
      return this.objectIDMap.set(t, r), this.nextID += 1, r;
    }
  }, {
    key: "clear",
    value: function() {
      var t = this;
      if (this.accessBeat > 1e4) {
        var r = Date.now();
        this.lastAccessBeat.forEach(function(i, o) {
          r - i > ss && (t.map.delete(o), t.lastAccessBeat.delete(o));
        }), this.accessBeat = 0;
      }
    }
  }]), n;
}(), In = new as();
function ls(n, e) {
  return f.useMemo(function() {
    var t = In.get(e);
    if (t)
      return t;
    var r = n();
    return In.set(e, r), r;
  }, e);
}
var cs = function() {
  return {};
};
function us(n) {
  var e = n.useCSP, t = e === void 0 ? cs : e, r = n.useToken, i = n.usePrefix, o = n.getResetStyles, s = n.getCommonStyle, a = n.getCompUnitless;
  function c(h, p, v, b) {
    var g = Array.isArray(h) ? h[0] : h;
    function m(P) {
      return "".concat(String(g)).concat(P.slice(0, 1).toUpperCase()).concat(P.slice(1));
    }
    var S = (b == null ? void 0 : b.unitless) || {}, C = typeof a == "function" ? a(h) : {}, y = D(D({}, C), {}, k({}, m("zIndexPopup"), !0));
    Object.keys(S).forEach(function(P) {
      y[m(P)] = S[P];
    });
    var x = D(D({}, b), {}, {
      unitless: y,
      prefixToken: m
    }), w = u(h, p, v, x), _ = l(g, v, x);
    return function(P) {
      var O = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : P, T = w(P, O), M = fe(T, 2), I = M[1], N = _(O), W = fe(N, 2), A = W[0], B = W[1];
      return [A, I, B];
    };
  }
  function l(h, p, v) {
    var b = v.unitless, g = v.injectStyle, m = g === void 0 ? !0 : g, S = v.prefixToken, C = v.ignore, y = function(_) {
      var P = _.rootCls, O = _.cssVar, T = O === void 0 ? {} : O, M = r(), I = M.realToken;
      return Ai({
        path: [h],
        prefix: T.prefix,
        key: T.key,
        unitless: b,
        ignore: C,
        token: I,
        scope: P
      }, function() {
        var N = kn(h, I, p), W = $n(h, I, N, {
          deprecatedTokens: v == null ? void 0 : v.deprecatedTokens
        });
        return Object.keys(N).forEach(function(A) {
          W[S(A)] = W[A], delete W[A];
        }), W;
      }), null;
    }, x = function(_) {
      var P = r(), O = P.cssVar;
      return [function(T) {
        return m && O ? /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement(y, {
          rootCls: _,
          cssVar: O,
          component: h
        }), T) : T;
      }, O == null ? void 0 : O.key];
    };
    return x;
  }
  function u(h, p, v) {
    var b = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(h) ? h : [h, h], m = fe(g, 1), S = m[0], C = g.join("-"), y = n.layer || {
      name: "antd"
    };
    return function(x) {
      var w = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : x, _ = r(), P = _.theme, O = _.realToken, T = _.hashId, M = _.token, I = _.cssVar, N = i(), W = N.rootPrefixCls, A = N.iconPrefixCls, B = t(), $ = I ? "css" : "js", H = ls(function() {
        var G = /* @__PURE__ */ new Set();
        return I && Object.keys(b.unitless || {}).forEach(function(Q) {
          G.add($t(Q, I.prefix)), G.add($t(Q, Ln(S, I.prefix)));
        }), Vo($, G);
      }, [$, S, I == null ? void 0 : I.prefix]), E = os($), ce = E.max, ee = E.min, F = {
        theme: P,
        token: M,
        hashId: T,
        nonce: function() {
          return B.nonce;
        },
        clientOnly: b.clientOnly,
        layer: y,
        // antd is always at top of styles
        order: b.order || -999
      };
      typeof o == "function" && mn(D(D({}, F), {}, {
        clientOnly: !1,
        path: ["Shared", W]
      }), function() {
        return o(M, {
          prefix: {
            rootPrefixCls: W,
            iconPrefixCls: A
          },
          csp: B
        });
      });
      var J = mn(D(D({}, F), {}, {
        path: [C, x, A]
      }), function() {
        if (b.injectStyle === !1)
          return [];
        var G = is(M), Q = G.token, ae = G.flush, he = kn(S, O, v), Se = ".".concat(x), z = $n(S, O, he, {
          deprecatedTokens: b.deprecatedTokens
        });
        I && he && le(he) === "object" && Object.keys(he).forEach(function(K) {
          he[K] = "var(".concat($t(K, Ln(S, I.prefix)), ")");
        });
        var L = Mt(Q, {
          componentCls: Se,
          prefixCls: x,
          iconCls: ".".concat(A),
          antCls: ".".concat(W),
          calc: H,
          // @ts-ignore
          max: ce,
          // @ts-ignore
          min: ee
        }, I ? he : z), j = p(L, {
          hashId: T,
          prefixCls: x,
          rootPrefixCls: W,
          iconPrefixCls: A
        });
        ae(S, z);
        var te = typeof s == "function" ? s(L, x, w, b.resetFont) : null;
        return [b.resetStyle === !1 ? null : te, j];
      });
      return [J, T];
    };
  }
  function d(h, p, v) {
    var b = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = u(h, p, v, D({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, b)), m = function(C) {
      var y = C.prefixCls, x = C.rootCls, w = x === void 0 ? y : x;
      return g(y, w), null;
    };
    return m;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: d,
    genComponentStyleHook: u
  };
}
const ds = {
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
}, fs = Object.assign(Object.assign({}, ds), {
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
}), se = Math.round;
function Ft(n, e) {
  const t = n.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], r = t.map((i) => parseFloat(i));
  for (let i = 0; i < 3; i += 1)
    r[i] = e(r[i] || 0, t[i] || "", i);
  return t[3] ? r[3] = t[3].includes("%") ? r[3] / 100 : r[3] : r[3] = 1, r;
}
const Nn = (n, e, t) => t === 0 ? n : n / 100;
function je(n, e) {
  const t = e || 255;
  return n > t ? t : n < 0 ? 0 : n;
}
class xe {
  constructor(e) {
    k(this, "isValid", !0), k(this, "r", 0), k(this, "g", 0), k(this, "b", 0), k(this, "a", 1), k(this, "_h", void 0), k(this, "_s", void 0), k(this, "_l", void 0), k(this, "_v", void 0), k(this, "_max", void 0), k(this, "_min", void 0), k(this, "_brightness", void 0);
    function t(r) {
      return r[0] in e && r[1] in e && r[2] in e;
    }
    if (e) if (typeof e == "string") {
      let i = function(o) {
        return r.startsWith(o);
      };
      const r = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(r) ? this.fromHexString(r) : i("rgb") ? this.fromRgbString(r) : i("hsl") ? this.fromHslString(r) : (i("hsv") || i("hsb")) && this.fromHsvString(r);
    } else if (e instanceof xe)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (t("rgb"))
      this.r = je(e.r), this.g = je(e.g), this.b = je(e.b), this.a = typeof e.a == "number" ? je(e.a, 1) : 1;
    else if (t("hsl"))
      this.fromHsl(e);
    else if (t("hsv"))
      this.fromHsv(e);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(e));
  }
  // ======================= Setter =======================
  setR(e) {
    return this._sc("r", e);
  }
  setG(e) {
    return this._sc("g", e);
  }
  setB(e) {
    return this._sc("b", e);
  }
  setA(e) {
    return this._sc("a", e, 1);
  }
  setHue(e) {
    const t = this.toHsv();
    return t.h = e, this._c(t);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function e(o) {
      const s = o / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const t = e(this.r), r = e(this.g), i = e(this.b);
    return 0.2126 * t + 0.7152 * r + 0.0722 * i;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = se(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._s = 0 : this._s = e / this.getMax();
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
  darken(e = 10) {
    const t = this.getHue(), r = this.getSaturation();
    let i = this.getLightness() - e / 100;
    return i < 0 && (i = 0), this._c({
      h: t,
      s: r,
      l: i,
      a: this.a
    });
  }
  lighten(e = 10) {
    const t = this.getHue(), r = this.getSaturation();
    let i = this.getLightness() + e / 100;
    return i > 1 && (i = 1), this._c({
      h: t,
      s: r,
      l: i,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(e, t = 50) {
    const r = this._c(e), i = t / 100, o = (a) => (r[a] - this[a]) * i + this[a], s = {
      r: se(o("r")),
      g: se(o("g")),
      b: se(o("b")),
      a: se(o("a") * 100) / 100
    };
    return this._c(s);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(e = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, e);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(e = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, e);
  }
  onBackground(e) {
    const t = this._c(e), r = this.a + t.a * (1 - this.a), i = (o) => se((this[o] * this.a + t[o] * t.a * (1 - this.a)) / r);
    return this._c({
      r: i("r"),
      g: i("g"),
      b: i("b"),
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
  equals(e) {
    return this.r === e.r && this.g === e.g && this.b === e.b && this.a === e.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let e = "#";
    const t = (this.r || 0).toString(16);
    e += t.length === 2 ? t : "0" + t;
    const r = (this.g || 0).toString(16);
    e += r.length === 2 ? r : "0" + r;
    const i = (this.b || 0).toString(16);
    if (e += i.length === 2 ? i : "0" + i, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const o = se(this.a * 255).toString(16);
      e += o.length === 2 ? o : "0" + o;
    }
    return e;
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
    const e = this.getHue(), t = se(this.getSaturation() * 100), r = se(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${e},${t}%,${r}%,${this.a})` : `hsl(${e},${t}%,${r}%)`;
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
  _sc(e, t, r) {
    const i = this.clone();
    return i[e] = je(t, r), i;
  }
  _c(e) {
    return new this.constructor(e);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(e) {
    const t = e.replace("#", "");
    function r(i, o) {
      return parseInt(t[i] + t[o || i], 16);
    }
    t.length < 6 ? (this.r = r(0), this.g = r(1), this.b = r(2), this.a = t[3] ? r(3) / 255 : 1) : (this.r = r(0, 1), this.g = r(2, 3), this.b = r(4, 5), this.a = t[6] ? r(6, 7) / 255 : 1);
  }
  fromHsl({
    h: e,
    s: t,
    l: r,
    a: i
  }) {
    if (this._h = e % 360, this._s = t, this._l = r, this.a = typeof i == "number" ? i : 1, t <= 0) {
      const h = se(r * 255);
      this.r = h, this.g = h, this.b = h;
    }
    let o = 0, s = 0, a = 0;
    const c = e / 60, l = (1 - Math.abs(2 * r - 1)) * t, u = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (o = l, s = u) : c >= 1 && c < 2 ? (o = u, s = l) : c >= 2 && c < 3 ? (s = l, a = u) : c >= 3 && c < 4 ? (s = u, a = l) : c >= 4 && c < 5 ? (o = u, a = l) : c >= 5 && c < 6 && (o = l, a = u);
    const d = r - l / 2;
    this.r = se((o + d) * 255), this.g = se((s + d) * 255), this.b = se((a + d) * 255);
  }
  fromHsv({
    h: e,
    s: t,
    v: r,
    a: i
  }) {
    this._h = e % 360, this._s = t, this._v = r, this.a = typeof i == "number" ? i : 1;
    const o = se(r * 255);
    if (this.r = o, this.g = o, this.b = o, t <= 0)
      return;
    const s = e / 60, a = Math.floor(s), c = s - a, l = se(r * (1 - t) * 255), u = se(r * (1 - t * c) * 255), d = se(r * (1 - t * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = d, this.b = l;
        break;
      case 1:
        this.r = u, this.b = l;
        break;
      case 2:
        this.r = l, this.b = d;
        break;
      case 3:
        this.r = l, this.g = u;
        break;
      case 4:
        this.r = d, this.g = l;
        break;
      case 5:
      default:
        this.g = l, this.b = u;
        break;
    }
  }
  fromHsvString(e) {
    const t = Ft(e, Nn);
    this.fromHsv({
      h: t[0],
      s: t[1],
      v: t[2],
      a: t[3]
    });
  }
  fromHslString(e) {
    const t = Ft(e, Nn);
    this.fromHsl({
      h: t[0],
      s: t[1],
      l: t[2],
      a: t[3]
    });
  }
  fromRgbString(e) {
    const t = Ft(e, (r, i) => (
      // Convert percentage to number. e.g. 50% -> 128
      i.includes("%") ? se(r / 100 * 255) : r
    ));
    this.r = t[0], this.g = t[1], this.b = t[2], this.a = t[3];
  }
}
function jt(n) {
  return n >= 0 && n <= 255;
}
function Ke(n, e) {
  const {
    r: t,
    g: r,
    b: i,
    a: o
  } = new xe(n).toRgb();
  if (o < 1)
    return n;
  const {
    r: s,
    g: a,
    b: c
  } = new xe(e).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const u = Math.round((t - s * (1 - l)) / l), d = Math.round((r - a * (1 - l)) / l), h = Math.round((i - c * (1 - l)) / l);
    if (jt(u) && jt(d) && jt(h))
      return new xe({
        r: u,
        g: d,
        b: h,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new xe({
    r: t,
    g: r,
    b: i,
    a: 1
  }).toRgbString();
}
var hs = function(n, e) {
  var t = {};
  for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && e.indexOf(r) < 0 && (t[r] = n[r]);
  if (n != null && typeof Object.getOwnPropertySymbols == "function") for (var i = 0, r = Object.getOwnPropertySymbols(n); i < r.length; i++)
    e.indexOf(r[i]) < 0 && Object.prototype.propertyIsEnumerable.call(n, r[i]) && (t[r[i]] = n[r[i]]);
  return t;
};
function ps(n) {
  const {
    override: e
  } = n, t = hs(n, ["override"]), r = Object.assign({}, e);
  Object.keys(fs).forEach((h) => {
    delete r[h];
  });
  const i = Object.assign(Object.assign({}, t), r), o = 480, s = 576, a = 768, c = 992, l = 1200, u = 1600;
  if (i.motion === !1) {
    const h = "0s";
    i.motionDurationFast = h, i.motionDurationMid = h, i.motionDurationSlow = h;
  }
  return Object.assign(Object.assign(Object.assign({}, i), {
    // ============== Background ============== //
    colorFillContent: i.colorFillSecondary,
    colorFillContentHover: i.colorFill,
    colorFillAlter: i.colorFillQuaternary,
    colorBgContainerDisabled: i.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: i.colorBgContainer,
    colorSplit: Ke(i.colorBorderSecondary, i.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: i.colorTextQuaternary,
    colorTextDisabled: i.colorTextQuaternary,
    colorTextHeading: i.colorText,
    colorTextLabel: i.colorTextSecondary,
    colorTextDescription: i.colorTextTertiary,
    colorTextLightSolid: i.colorWhite,
    colorHighlight: i.colorError,
    colorBgTextHover: i.colorFillSecondary,
    colorBgTextActive: i.colorFill,
    colorIcon: i.colorTextTertiary,
    colorIconHover: i.colorText,
    colorErrorOutline: Ke(i.colorErrorBg, i.colorBgContainer),
    colorWarningOutline: Ke(i.colorWarningBg, i.colorBgContainer),
    // Font
    fontSizeIcon: i.fontSizeSM,
    // Line
    lineWidthFocus: i.lineWidth * 3,
    // Control
    lineWidth: i.lineWidth,
    controlOutlineWidth: i.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: i.controlHeight / 2,
    controlItemBgHover: i.colorFillTertiary,
    controlItemBgActive: i.colorPrimaryBg,
    controlItemBgActiveHover: i.colorPrimaryBgHover,
    controlItemBgActiveDisabled: i.colorFill,
    controlTmpOutline: i.colorFillQuaternary,
    controlOutline: Ke(i.colorPrimaryBg, i.colorBgContainer),
    lineType: i.lineType,
    borderRadius: i.borderRadius,
    borderRadiusXS: i.borderRadiusXS,
    borderRadiusSM: i.borderRadiusSM,
    borderRadiusLG: i.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: i.sizeXXS,
    paddingXS: i.sizeXS,
    paddingSM: i.sizeSM,
    padding: i.size,
    paddingMD: i.sizeMD,
    paddingLG: i.sizeLG,
    paddingXL: i.sizeXL,
    paddingContentHorizontalLG: i.sizeLG,
    paddingContentVerticalLG: i.sizeMS,
    paddingContentHorizontal: i.sizeMS,
    paddingContentVertical: i.sizeSM,
    paddingContentHorizontalSM: i.size,
    paddingContentVerticalSM: i.sizeXS,
    marginXXS: i.sizeXXS,
    marginXS: i.sizeXS,
    marginSM: i.sizeSM,
    margin: i.size,
    marginMD: i.sizeMD,
    marginLG: i.sizeLG,
    marginXL: i.sizeXL,
    marginXXL: i.sizeXXL,
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
    screenXS: o,
    screenXSMin: o,
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
    screenXLMax: u - 1,
    screenXXL: u,
    screenXXLMin: u,
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
const ms = {
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
}, gs = {
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
}, vs = $i(dt.defaultAlgorithm), bs = {
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
}, yr = (n, e, t) => {
  const r = t.getDerivativeToken(n), {
    override: i,
    ...o
  } = e;
  let s = {
    ...r,
    override: i
  };
  return s = ps(s), o && Object.entries(o).forEach(([a, c]) => {
    const {
      theme: l,
      ...u
    } = c;
    let d = u;
    l && (d = yr({
      ...s,
      ...u
    }, {
      override: u
    }, l)), s[a] = d;
  }), s;
};
function ys() {
  const {
    token: n,
    hashed: e,
    theme: t = vs,
    override: r,
    cssVar: i
  } = f.useContext(dt._internalContext), [o, s, a] = Di(t, [dt.defaultSeed, n], {
    salt: `${Ro}-${e || ""}`,
    override: r,
    getComputedToken: yr,
    cssVar: i && {
      prefix: i.prefix,
      key: i.key,
      unitless: ms,
      ignore: gs,
      preserve: bs
    }
  });
  return [t, a, e ? s : "", o, i];
}
const {
  genStyleHooks: wr
} = us({
  usePrefix: () => {
    const {
      getPrefixCls: n,
      iconPrefixCls: e
    } = Ve();
    return {
      iconPrefixCls: e,
      rootPrefixCls: n()
    };
  },
  useToken: () => {
    const [n, e, t, r, i] = ys();
    return {
      theme: n,
      realToken: e,
      hashId: t,
      token: r,
      cssVar: i
    };
  },
  useCSP: () => {
    const {
      csp: n
    } = Ve();
    return n ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), Xe = /* @__PURE__ */ f.createContext(null);
function Wn(n) {
  const {
    getDropContainer: e,
    className: t,
    prefixCls: r,
    children: i
  } = n, {
    disabled: o
  } = f.useContext(Xe), [s, a] = f.useState(), [c, l] = f.useState(null);
  if (f.useEffect(() => {
    const h = e == null ? void 0 : e();
    s !== h && a(h);
  }, [e]), f.useEffect(() => {
    if (s) {
      const h = () => {
        l(!0);
      }, p = (g) => {
        g.preventDefault();
      }, v = (g) => {
        g.relatedTarget || l(!1);
      }, b = (g) => {
        l(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", h), document.addEventListener("dragover", p), document.addEventListener("dragleave", v), document.addEventListener("drop", b), () => {
        document.removeEventListener("dragenter", h), document.removeEventListener("dragover", p), document.removeEventListener("dragleave", v), document.removeEventListener("drop", b);
      };
    }
  }, [!!s]), !(e && s && !o))
    return null;
  const d = `${r}-drop-area`;
  return /* @__PURE__ */ ut(/* @__PURE__ */ f.createElement("div", {
    className: Z(d, t, {
      [`${d}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: c ? "block" : "none"
    }
  }, i), s);
}
function Fn(n) {
  return n instanceof HTMLElement || n instanceof SVGElement;
}
function ws(n) {
  return n && le(n) === "object" && Fn(n.nativeElement) ? n.nativeElement : Fn(n) ? n : null;
}
function Ss(n) {
  var e = ws(n);
  if (e)
    return e;
  if (n instanceof f.Component) {
    var t;
    return (t = pn.findDOMNode) === null || t === void 0 ? void 0 : t.call(pn, n);
  }
  return null;
}
function xs(n, e) {
  if (n == null) return {};
  var t = {};
  for (var r in n) if ({}.hasOwnProperty.call(n, r)) {
    if (e.indexOf(r) !== -1) continue;
    t[r] = n[r];
  }
  return t;
}
function jn(n, e) {
  if (n == null) return {};
  var t, r, i = xs(n, e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(n);
    for (r = 0; r < o.length; r++) t = o[r], e.indexOf(t) === -1 && {}.propertyIsEnumerable.call(n, t) && (i[t] = n[t]);
  }
  return i;
}
var Cs = /* @__PURE__ */ R.createContext({}), Es = /* @__PURE__ */ function(n) {
  gt(t, n);
  var e = vt(t);
  function t() {
    return Ie(this, t), e.apply(this, arguments);
  }
  return Ne(t, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), t;
}(R.Component);
function _s(n) {
  var e = R.useReducer(function(a) {
    return a + 1;
  }, 0), t = fe(e, 2), r = t[1], i = R.useRef(n), o = _e(function() {
    return i.current;
  }), s = _e(function(a) {
    i.current = typeof a == "function" ? a(i.current) : a, r();
  });
  return [o, s];
}
var Ee = "none", Ye = "appear", Ze = "enter", Qe = "leave", Bn = "none", we = "prepare", Oe = "start", Ae = "active", dn = "end", Sr = "prepared";
function Hn(n, e) {
  var t = {};
  return t[n.toLowerCase()] = e.toLowerCase(), t["Webkit".concat(n)] = "webkit".concat(e), t["Moz".concat(n)] = "moz".concat(e), t["ms".concat(n)] = "MS".concat(e), t["O".concat(n)] = "o".concat(e.toLowerCase()), t;
}
function Rs(n, e) {
  var t = {
    animationend: Hn("Animation", "AnimationEnd"),
    transitionend: Hn("Transition", "TransitionEnd")
  };
  return n && ("AnimationEvent" in e || delete t.animationend.animation, "TransitionEvent" in e || delete t.transitionend.transition), t;
}
var Ts = Rs(bt(), typeof window < "u" ? window : {}), xr = {};
if (bt()) {
  var Ps = document.createElement("div");
  xr = Ps.style;
}
var Je = {};
function Cr(n) {
  if (Je[n])
    return Je[n];
  var e = Ts[n];
  if (e)
    for (var t = Object.keys(e), r = t.length, i = 0; i < r; i += 1) {
      var o = t[i];
      if (Object.prototype.hasOwnProperty.call(e, o) && o in xr)
        return Je[n] = e[o], Je[n];
    }
  return "";
}
var Er = Cr("animationend"), _r = Cr("transitionend"), Rr = !!(Er && _r), zn = Er || "animationend", Vn = _r || "transitionend";
function Un(n, e) {
  if (!n) return null;
  if (le(n) === "object") {
    var t = e.replace(/-\w/g, function(r) {
      return r[1].toUpperCase();
    });
    return n[t];
  }
  return "".concat(n, "-").concat(e);
}
const Ms = function(n) {
  var e = pe();
  function t(i) {
    i && (i.removeEventListener(Vn, n), i.removeEventListener(zn, n));
  }
  function r(i) {
    e.current && e.current !== i && t(e.current), i && i !== e.current && (i.addEventListener(Vn, n), i.addEventListener(zn, n), e.current = i);
  }
  return R.useEffect(function() {
    return function() {
      t(e.current);
    };
  }, []), [r, t];
};
var Tr = bt() ? qr : Ce, Pr = function(e) {
  return +setTimeout(e, 16);
}, Mr = function(e) {
  return clearTimeout(e);
};
typeof window < "u" && "requestAnimationFrame" in window && (Pr = function(e) {
  return window.requestAnimationFrame(e);
}, Mr = function(e) {
  return window.cancelAnimationFrame(e);
});
var Xn = 0, fn = /* @__PURE__ */ new Map();
function Lr(n) {
  fn.delete(n);
}
var Jt = function(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  Xn += 1;
  var r = Xn;
  function i(o) {
    if (o === 0)
      Lr(r), e();
    else {
      var s = Pr(function() {
        i(o - 1);
      });
      fn.set(r, s);
    }
  }
  return i(t), r;
};
Jt.cancel = function(n) {
  var e = fn.get(n);
  return Lr(n), Mr(e);
};
const Ls = function() {
  var n = R.useRef(null);
  function e() {
    Jt.cancel(n.current);
  }
  function t(r) {
    var i = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    e();
    var o = Jt(function() {
      i <= 1 ? r({
        isCanceled: function() {
          return o !== n.current;
        }
      }) : t(r, i - 1);
    });
    n.current = o;
  }
  return R.useEffect(function() {
    return function() {
      e();
    };
  }, []), [t, e];
};
var Os = [we, Oe, Ae, dn], As = [we, Sr], Or = !1, $s = !0;
function Ar(n) {
  return n === Ae || n === dn;
}
const Ds = function(n, e, t) {
  var r = Ue(Bn), i = fe(r, 2), o = i[0], s = i[1], a = Ls(), c = fe(a, 2), l = c[0], u = c[1];
  function d() {
    s(we, !0);
  }
  var h = e ? As : Os;
  return Tr(function() {
    if (o !== Bn && o !== dn) {
      var p = h.indexOf(o), v = h[p + 1], b = t(o);
      b === Or ? s(v, !0) : v && l(function(g) {
        function m() {
          g.isCanceled() || s(v, !0);
        }
        b === !0 ? m() : Promise.resolve(b).then(m);
      });
    }
  }, [n, o]), R.useEffect(function() {
    return function() {
      u();
    };
  }, []), [d, o];
};
function ks(n, e, t, r) {
  var i = r.motionEnter, o = i === void 0 ? !0 : i, s = r.motionAppear, a = s === void 0 ? !0 : s, c = r.motionLeave, l = c === void 0 ? !0 : c, u = r.motionDeadline, d = r.motionLeaveImmediately, h = r.onAppearPrepare, p = r.onEnterPrepare, v = r.onLeavePrepare, b = r.onAppearStart, g = r.onEnterStart, m = r.onLeaveStart, S = r.onAppearActive, C = r.onEnterActive, y = r.onLeaveActive, x = r.onAppearEnd, w = r.onEnterEnd, _ = r.onLeaveEnd, P = r.onVisibleChanged, O = Ue(), T = fe(O, 2), M = T[0], I = T[1], N = _s(Ee), W = fe(N, 2), A = W[0], B = W[1], $ = Ue(null), H = fe($, 2), E = H[0], ce = H[1], ee = A(), F = pe(!1), J = pe(null);
  function G() {
    return t();
  }
  var Q = pe(!1);
  function ae() {
    B(Ee), ce(null, !0);
  }
  var he = _e(function(re) {
    var ie = A();
    if (ie !== Ee) {
      var ue = G();
      if (!(re && !re.deadline && re.target !== ue)) {
        var Pe = Q.current, Re;
        ie === Ye && Pe ? Re = x == null ? void 0 : x(ue, re) : ie === Ze && Pe ? Re = w == null ? void 0 : w(ue, re) : ie === Qe && Pe && (Re = _ == null ? void 0 : _(ue, re)), Pe && Re !== !1 && ae();
      }
    }
  }), Se = Ms(he), z = fe(Se, 1), L = z[0], j = function(ie) {
    switch (ie) {
      case Ye:
        return k(k(k({}, we, h), Oe, b), Ae, S);
      case Ze:
        return k(k(k({}, we, p), Oe, g), Ae, C);
      case Qe:
        return k(k(k({}, we, v), Oe, m), Ae, y);
      default:
        return {};
    }
  }, te = R.useMemo(function() {
    return j(ee);
  }, [ee]), K = Ds(ee, !n, function(re) {
    if (re === we) {
      var ie = te[we];
      return ie ? ie(G()) : Or;
    }
    if (oe in te) {
      var ue;
      ce(((ue = te[oe]) === null || ue === void 0 ? void 0 : ue.call(te, G(), null)) || null);
    }
    return oe === Ae && ee !== Ee && (L(G()), u > 0 && (clearTimeout(J.current), J.current = setTimeout(function() {
      he({
        deadline: !0
      });
    }, u))), oe === Sr && ae(), $s;
  }), ne = fe(K, 2), me = ne[0], oe = ne[1], U = Ar(oe);
  Q.current = U;
  var ge = pe(null);
  Tr(function() {
    if (!(F.current && ge.current === e)) {
      I(e);
      var re = F.current;
      F.current = !0;
      var ie;
      !re && e && a && (ie = Ye), re && e && o && (ie = Ze), (re && !e && l || !re && d && !e && l) && (ie = Qe);
      var ue = j(ie);
      ie && (n || ue[we]) ? (B(ie), me()) : B(Ee), ge.current = e;
    }
  }, [e]), Ce(function() {
    // Cancel appear
    (ee === Ye && !a || // Cancel enter
    ee === Ze && !o || // Cancel leave
    ee === Qe && !l) && B(Ee);
  }, [a, o, l]), Ce(function() {
    return function() {
      F.current = !1, clearTimeout(J.current);
    };
  }, []);
  var ye = R.useRef(!1);
  Ce(function() {
    M && (ye.current = !0), M !== void 0 && ee === Ee && ((ye.current || M) && (P == null || P(M)), ye.current = !0);
  }, [M, ee]);
  var X = E;
  return te[we] && oe === Oe && (X = D({
    transition: "none"
  }, X)), [ee, oe, X, M ?? e];
}
function Is(n) {
  var e = n;
  le(n) === "object" && (e = n.transitionSupport);
  function t(i, o) {
    return !!(i.motionName && e && o !== !1);
  }
  var r = /* @__PURE__ */ R.forwardRef(function(i, o) {
    var s = i.visible, a = s === void 0 ? !0 : s, c = i.removeOnLeave, l = c === void 0 ? !0 : c, u = i.forceRender, d = i.children, h = i.motionName, p = i.leavedClassName, v = i.eventProps, b = R.useContext(Cs), g = b.motion, m = t(i, g), S = pe(), C = pe();
    function y() {
      try {
        return S.current instanceof HTMLElement ? S.current : Ss(C.current);
      } catch {
        return null;
      }
    }
    var x = ks(m, a, y, i), w = fe(x, 4), _ = w[0], P = w[1], O = w[2], T = w[3], M = R.useRef(T);
    T && (M.current = !0);
    var I = R.useCallback(function(H) {
      S.current = H, Jo(o, H);
    }, [o]), N, W = D(D({}, v), {}, {
      visible: a
    });
    if (!d)
      N = null;
    else if (_ === Ee)
      T ? N = d(D({}, W), I) : !l && M.current && p ? N = d(D(D({}, W), {}, {
        className: p
      }), I) : u || !l && !p ? N = d(D(D({}, W), {}, {
        style: {
          display: "none"
        }
      }), I) : N = null;
    else {
      var A;
      P === we ? A = "prepare" : Ar(P) ? A = "active" : P === Oe && (A = "start");
      var B = Un(h, "".concat(_, "-").concat(A));
      N = d(D(D({}, W), {}, {
        className: Z(Un(h, _), k(k({}, B, B && A), h, typeof h == "string")),
        style: O
      }), I);
    }
    if (/* @__PURE__ */ R.isValidElement(N) && es(N)) {
      var $ = ts(N);
      $ || (N = /* @__PURE__ */ R.cloneElement(N, {
        ref: I
      }));
    }
    return /* @__PURE__ */ R.createElement(Es, {
      ref: C
    }, N);
  });
  return r.displayName = "CSSMotion", r;
}
const $r = Is(Rr);
var en = "add", tn = "keep", nn = "remove", Bt = "removed";
function Ns(n) {
  var e;
  return n && le(n) === "object" && "key" in n ? e = n : e = {
    key: n
  }, D(D({}, e), {}, {
    key: String(e.key)
  });
}
function rn() {
  var n = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return n.map(Ns);
}
function Ws() {
  var n = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], t = [], r = 0, i = e.length, o = rn(n), s = rn(e);
  o.forEach(function(l) {
    for (var u = !1, d = r; d < i; d += 1) {
      var h = s[d];
      if (h.key === l.key) {
        r < d && (t = t.concat(s.slice(r, d).map(function(p) {
          return D(D({}, p), {}, {
            status: en
          });
        })), r = d), t.push(D(D({}, h), {}, {
          status: tn
        })), r += 1, u = !0;
        break;
      }
    }
    u || t.push(D(D({}, l), {}, {
      status: nn
    }));
  }), r < i && (t = t.concat(s.slice(r).map(function(l) {
    return D(D({}, l), {}, {
      status: en
    });
  })));
  var a = {};
  t.forEach(function(l) {
    var u = l.key;
    a[u] = (a[u] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(l) {
    return a[l] > 1;
  });
  return c.forEach(function(l) {
    t = t.filter(function(u) {
      var d = u.key, h = u.status;
      return d !== l || h !== nn;
    }), t.forEach(function(u) {
      u.key === l && (u.status = tn);
    });
  }), t;
}
var Fs = ["component", "children", "onVisibleChanged", "onAllRemoved"], js = ["status"], Bs = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function Hs(n) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : $r, t = /* @__PURE__ */ function(r) {
    gt(o, r);
    var i = vt(o);
    function o() {
      var s;
      Ie(this, o);
      for (var a = arguments.length, c = new Array(a), l = 0; l < a; l++)
        c[l] = arguments[l];
      return s = i.call.apply(i, [this].concat(c)), k(Te(s), "state", {
        keyEntities: []
      }), k(Te(s), "removeKey", function(u) {
        s.setState(function(d) {
          var h = d.keyEntities.map(function(p) {
            return p.key !== u ? p : D(D({}, p), {}, {
              status: Bt
            });
          });
          return {
            keyEntities: h
          };
        }, function() {
          var d = s.state.keyEntities, h = d.filter(function(p) {
            var v = p.status;
            return v !== Bt;
          }).length;
          h === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Ne(o, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, l = this.props, u = l.component, d = l.children, h = l.onVisibleChanged;
        l.onAllRemoved;
        var p = jn(l, Fs), v = u || R.Fragment, b = {};
        return Bs.forEach(function(g) {
          b[g] = p[g], delete p[g];
        }), delete p.keys, /* @__PURE__ */ R.createElement(v, p, c.map(function(g, m) {
          var S = g.status, C = jn(g, js), y = S === en || S === tn;
          return /* @__PURE__ */ R.createElement(e, ve({}, b, {
            key: C.key,
            visible: y,
            eventProps: C,
            onVisibleChanged: function(w) {
              h == null || h(w, {
                key: C.key
              }), w || a.removeKey(C.key);
            }
          }), function(x, w) {
            return d(D(D({}, x), {}, {
              index: m
            }), w);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var l = a.keys, u = c.keyEntities, d = rn(l), h = Ws(u, d);
        return {
          keyEntities: h.filter(function(p) {
            var v = u.find(function(b) {
              var g = b.key;
              return p.key === g;
            });
            return !(v && v.status === Bt && p.status === nn);
          })
        };
      }
    }]), o;
  }(R.Component);
  return k(t, "defaultProps", {
    component: "div"
  }), t;
}
const zs = Hs(Rr);
function Vs(n, e) {
  const {
    children: t,
    upload: r,
    rootClassName: i
  } = n, o = f.useRef(null);
  return f.useImperativeHandle(e, () => o.current), /* @__PURE__ */ f.createElement(rr, ve({}, r, {
    showUploadList: !1,
    rootClassName: i,
    ref: o
  }), t);
}
const Dr = /* @__PURE__ */ f.forwardRef(Vs), Us = (n) => {
  const {
    componentCls: e,
    antCls: t,
    calc: r
  } = n, i = `${e}-list-card`, o = r(n.fontSize).mul(n.lineHeight).mul(2).add(n.paddingSM).add(n.paddingSM).equal();
  return {
    [i]: {
      borderRadius: n.borderRadius,
      position: "relative",
      background: n.colorFillContent,
      borderWidth: n.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${i}-name,${i}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${i}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${i}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: r(n.paddingSM).sub(n.lineWidth).equal(),
        paddingInlineStart: r(n.padding).add(n.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: n.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${i}-icon`]: {
          fontSize: r(n.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: r(n.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${i}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${i}-desc`]: {
          color: n.colorTextTertiary
        }
      },
      // ============================== Preview ==============================
      "&-type-preview": {
        width: o,
        height: o,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${i}-status-error)`]: {
          border: 0
        },
        // Img
        [`${t}-image`]: {
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
        [`${i}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${n.opacityLoading})`
        },
        // Error
        [`&${i}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${i}-img-mask`]: {
            borderRadius: r(n.borderRadius).sub(n.lineWidth).equal()
          },
          [`${i}-desc`]: {
            paddingInline: n.paddingXXS
          }
        },
        // Progress
        [`${i}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${i}-remove`]: {
        position: "absolute",
        top: 0,
        insetInlineEnd: 0,
        border: 0,
        padding: n.paddingXXS,
        background: "transparent",
        lineHeight: 1,
        transform: "translate(50%, -50%)",
        fontSize: n.fontSize,
        cursor: "pointer",
        opacity: n.opacityLoading,
        display: "none",
        "&:dir(rtl)": {
          transform: "translate(-50%, -50%)"
        },
        "&:hover": {
          opacity: 1
        },
        "&:active": {
          opacity: n.opacityLoading
        }
      },
      [`&:hover ${i}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: n.colorError,
        [`${i}-desc`]: {
          color: n.colorError
        }
      },
      // ============================== Motion ===============================
      "&-motion": {
        transition: ["opacity", "width", "margin", "padding"].map((s) => `${s} ${n.motionDurationSlow}`).join(","),
        "&-appear-start": {
          width: 0,
          transition: "none"
        },
        "&-leave-active": {
          opacity: 0,
          width: 0,
          paddingInline: 0,
          borderInlineWidth: 0,
          marginInlineEnd: r(n.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, on = {
  "&, *": {
    boxSizing: "border-box"
  }
}, Xs = (n) => {
  const {
    componentCls: e,
    calc: t,
    antCls: r
  } = n, i = `${e}-drop-area`, o = `${e}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [i]: {
      position: "absolute",
      inset: 0,
      zIndex: n.zIndexPopupBase,
      ...on,
      "&-on-body": {
        position: "fixed",
        inset: 0
      },
      "&-hide-placement": {
        [`${o}-inner`]: {
          display: "none"
        }
      },
      [o]: {
        padding: 0
      }
    },
    "&": {
      // ============================= Placeholder =============================
      [o]: {
        height: "100%",
        borderRadius: n.borderRadius,
        borderWidth: n.lineWidthBold,
        borderStyle: "dashed",
        borderColor: "transparent",
        padding: n.padding,
        position: "relative",
        backdropFilter: "blur(10px)",
        background: n.colorBgPlaceholderHover,
        ...on,
        [`${r}-upload-wrapper ${r}-upload${r}-upload-btn`]: {
          padding: 0
        },
        [`&${o}-drag-in`]: {
          borderColor: n.colorPrimaryHover
        },
        [`&${o}-disabled`]: {
          opacity: 0.25,
          pointerEvents: "none"
        },
        [`${o}-inner`]: {
          gap: t(n.paddingXXS).div(2).equal()
        },
        [`${o}-icon`]: {
          fontSize: n.fontSizeHeading2,
          lineHeight: 1
        },
        [`${o}-title${o}-title`]: {
          margin: 0,
          fontSize: n.fontSize,
          lineHeight: n.lineHeight
        },
        [`${o}-description`]: {}
      }
    }
  };
}, Gs = (n) => {
  const {
    componentCls: e,
    calc: t
  } = n, r = `${e}-list`, i = t(n.fontSize).mul(n.lineHeight).mul(2).add(n.paddingSM).add(n.paddingSM).equal();
  return {
    [e]: {
      position: "relative",
      width: "100%",
      ...on,
      // =============================== File List ===============================
      [r]: {
        display: "flex",
        flexWrap: "wrap",
        gap: n.paddingSM,
        fontSize: n.fontSize,
        lineHeight: n.lineHeight,
        color: n.colorText,
        paddingBlock: n.paddingSM,
        paddingInline: n.padding,
        width: "100%",
        background: n.colorBgContainer,
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
            transition: `opacity ${n.motionDurationSlow}`,
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
          maxHeight: t(i).mul(3).equal(),
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
          width: i,
          height: i,
          fontSize: n.fontSizeHeading2,
          color: "#999"
        },
        // ======================================================================
        // ==                             PrevNext                             ==
        // ======================================================================
        "&-prev-btn, &-next-btn": {
          position: "absolute",
          top: "50%",
          transform: "translateY(-50%)",
          boxShadow: n.boxShadowTertiary,
          opacity: 0,
          pointerEvents: "none"
        },
        "&-prev-btn": {
          left: {
            _skip_check_: !0,
            value: n.padding
          }
        },
        "&-next-btn": {
          right: {
            _skip_check_: !0,
            value: n.padding
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
}, qs = (n) => {
  const {
    colorBgContainer: e
  } = n;
  return {
    colorBgPlaceholderHover: new xe(e).setA(0.85).toRgbString()
  };
}, kr = wr("Attachments", (n) => {
  const e = Mt(n, {});
  return [Xs(e), Gs(e), Us(e)];
}, qs), Ks = (n) => n.indexOf("image/") === 0, et = 200;
function Ys(n) {
  return new Promise((e) => {
    if (!n || !n.type || !Ks(n.type)) {
      e("");
      return;
    }
    const t = new Image();
    if (t.onload = () => {
      const {
        width: r,
        height: i
      } = t, o = r / i, s = o > 1 ? et : et * o, a = o > 1 ? et / o : et, c = document.createElement("canvas");
      c.width = s, c.height = a, c.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(c), c.getContext("2d").drawImage(t, 0, 0, s, a);
      const u = c.toDataURL();
      document.body.removeChild(c), window.URL.revokeObjectURL(t.src), e(u);
    }, t.crossOrigin = "anonymous", n.type.startsWith("image/svg+xml")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && typeof r.result == "string" && (t.src = r.result);
      }, r.readAsDataURL(n);
    } else if (n.type.startsWith("image/gif")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && e(r.result);
      }, r.readAsDataURL(n);
    } else
      t.src = window.URL.createObjectURL(n);
  });
}
function Zs() {
  return /* @__PURE__ */ f.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ f.createElement("title", null, "audio"), /* @__PURE__ */ f.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ f.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function Qs(n) {
  const {
    percent: e
  } = n, {
    token: t
  } = dt.useToken();
  return /* @__PURE__ */ f.createElement(Ti, {
    type: "circle",
    percent: e,
    size: t.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (r) => /* @__PURE__ */ f.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (r || 0).toFixed(0), "%")
  });
}
function Js() {
  return /* @__PURE__ */ f.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ f.createElement("title", null, "video"), /* @__PURE__ */ f.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ f.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const Ht = " ", sn = "#8c8c8c", Ir = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], ea = [{
  icon: /* @__PURE__ */ f.createElement(ci, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  icon: /* @__PURE__ */ f.createElement(ui, null),
  color: sn,
  ext: Ir
}, {
  icon: /* @__PURE__ */ f.createElement(di, null),
  color: sn,
  ext: ["md", "mdx"]
}, {
  icon: /* @__PURE__ */ f.createElement(fi, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  icon: /* @__PURE__ */ f.createElement(hi, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  icon: /* @__PURE__ */ f.createElement(pi, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  icon: /* @__PURE__ */ f.createElement(mi, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  icon: /* @__PURE__ */ f.createElement(Js, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  icon: /* @__PURE__ */ f.createElement(Zs, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function Gn(n, e) {
  return e.some((t) => n.toLowerCase() === `.${t}`);
}
function ta(n) {
  let e = n;
  const t = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let r = 0;
  for (; e >= 1024 && r < t.length - 1; )
    e /= 1024, r++;
  return `${e.toFixed(0)} ${t[r]}`;
}
function na(n, e) {
  const {
    prefixCls: t,
    item: r,
    onRemove: i,
    className: o,
    style: s,
    imageProps: a
  } = n, c = f.useContext(Xe), {
    disabled: l
  } = c || {}, {
    name: u,
    size: d,
    percent: h,
    status: p = "done",
    description: v
  } = r, {
    getPrefixCls: b
  } = Ve(), g = b("attachment", t), m = `${g}-list-card`, [S, C, y] = kr(g), [x, w] = f.useMemo(() => {
    const B = u || "", $ = B.match(/^(.*)\.[^.]+$/);
    return $ ? [$[1], B.slice($[1].length)] : [B, ""];
  }, [u]), _ = f.useMemo(() => Gn(w, Ir), [w]), P = f.useMemo(() => v || (p === "uploading" ? `${h || 0}%` : p === "error" ? r.response || Ht : d ? ta(d) : Ht), [p, h]), [O, T] = f.useMemo(() => {
    for (const {
      ext: B,
      icon: $,
      color: H
    } of ea)
      if (Gn(w, B))
        return [$, H];
    return [/* @__PURE__ */ f.createElement(ai, {
      key: "defaultIcon"
    }), sn];
  }, [w]), [M, I] = f.useState();
  f.useEffect(() => {
    if (r.originFileObj) {
      let B = !0;
      return Ys(r.originFileObj).then(($) => {
        B && I($);
      }), () => {
        B = !1;
      };
    }
    I(void 0);
  }, [r.originFileObj]);
  let N = null;
  const W = r.thumbUrl || r.url || M, A = _ && (r.originFileObj || W);
  return A ? N = /* @__PURE__ */ f.createElement(f.Fragment, null, W && /* @__PURE__ */ f.createElement(Pi, ve({
    alt: "preview",
    src: W
  }, a)), p !== "done" && /* @__PURE__ */ f.createElement("div", {
    className: `${m}-img-mask`
  }, p === "uploading" && h !== void 0 && /* @__PURE__ */ f.createElement(Qs, {
    percent: h,
    prefixCls: m
  }), p === "error" && /* @__PURE__ */ f.createElement("div", {
    className: `${m}-desc`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${m}-ellipsis-prefix`
  }, P)))) : N = /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement("div", {
    className: `${m}-icon`,
    style: {
      color: T
    }
  }, O), /* @__PURE__ */ f.createElement("div", {
    className: `${m}-content`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${m}-name`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${m}-ellipsis-prefix`
  }, x ?? Ht), /* @__PURE__ */ f.createElement("div", {
    className: `${m}-ellipsis-suffix`
  }, w)), /* @__PURE__ */ f.createElement("div", {
    className: `${m}-desc`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${m}-ellipsis-prefix`
  }, P)))), S(/* @__PURE__ */ f.createElement("div", {
    className: Z(m, {
      [`${m}-status-${p}`]: p,
      [`${m}-type-preview`]: A,
      [`${m}-type-overview`]: !A
    }, o, C, y),
    style: s,
    ref: e
  }, N, !l && i && /* @__PURE__ */ f.createElement("button", {
    type: "button",
    className: `${m}-remove`,
    onClick: () => {
      i(r);
    }
  }, /* @__PURE__ */ f.createElement(li, null))));
}
const Nr = /* @__PURE__ */ f.forwardRef(na), qn = 1;
function ra(n) {
  const {
    prefixCls: e,
    items: t,
    onRemove: r,
    overflow: i,
    upload: o,
    listClassName: s,
    listStyle: a,
    itemClassName: c,
    uploadClassName: l,
    uploadStyle: u,
    itemStyle: d,
    imageProps: h
  } = n, p = `${e}-list`, v = f.useRef(null), [b, g] = f.useState(!1), {
    disabled: m
  } = f.useContext(Xe);
  f.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [S, C] = f.useState(!1), [y, x] = f.useState(!1), w = () => {
    const T = v.current;
    T && (i === "scrollX" ? (C(Math.abs(T.scrollLeft) >= qn), x(T.scrollWidth - T.clientWidth - Math.abs(T.scrollLeft) >= qn)) : i === "scrollY" && (C(T.scrollTop !== 0), x(T.scrollHeight - T.clientHeight !== T.scrollTop)));
  };
  f.useEffect(() => {
    w();
  }, [i, t.length]);
  const _ = (T) => {
    const M = v.current;
    M && M.scrollTo({
      left: M.scrollLeft + T * M.clientWidth,
      behavior: "smooth"
    });
  }, P = () => {
    _(-1);
  }, O = () => {
    _(1);
  };
  return /* @__PURE__ */ f.createElement("div", {
    className: Z(p, {
      [`${p}-overflow-${n.overflow}`]: i,
      [`${p}-overflow-ping-start`]: S,
      [`${p}-overflow-ping-end`]: y
    }, s),
    ref: v,
    onScroll: w,
    style: a
  }, /* @__PURE__ */ f.createElement(zs, {
    keys: t.map((T) => ({
      key: T.uid,
      item: T
    })),
    motionName: `${p}-card-motion`,
    component: !1,
    motionAppear: b,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: T,
    item: M,
    className: I,
    style: N
  }) => /* @__PURE__ */ f.createElement(Nr, {
    key: T,
    prefixCls: e,
    item: M,
    onRemove: r,
    className: Z(I, c),
    imageProps: h,
    style: {
      ...N,
      ...d
    }
  })), !m && /* @__PURE__ */ f.createElement(Dr, {
    upload: o
  }, /* @__PURE__ */ f.createElement(De, {
    className: Z(l, `${p}-upload-btn`),
    style: u,
    type: "dashed"
  }, /* @__PURE__ */ f.createElement(gi, {
    className: `${p}-upload-btn-icon`
  }))), i === "scrollX" && /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement(De, {
    size: "small",
    shape: "circle",
    className: `${p}-prev-btn`,
    icon: /* @__PURE__ */ f.createElement(vi, null),
    onClick: P
  }), /* @__PURE__ */ f.createElement(De, {
    size: "small",
    shape: "circle",
    className: `${p}-next-btn`,
    icon: /* @__PURE__ */ f.createElement(bi, null),
    onClick: O
  })));
}
function ia(n, e) {
  const {
    prefixCls: t,
    placeholder: r = {},
    upload: i,
    className: o,
    style: s
  } = n, a = `${t}-placeholder`, c = r || {}, {
    disabled: l
  } = f.useContext(Xe), [u, d] = f.useState(!1), h = () => {
    d(!0);
  }, p = (g) => {
    g.currentTarget.contains(g.relatedTarget) || d(!1);
  }, v = () => {
    d(!1);
  }, b = /* @__PURE__ */ f.isValidElement(r) ? r : /* @__PURE__ */ f.createElement(ft, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ f.createElement(At.Text, {
    className: `${a}-icon`
  }, c.icon), /* @__PURE__ */ f.createElement(At.Title, {
    className: `${a}-title`,
    level: 5
  }, c.title), /* @__PURE__ */ f.createElement(At.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, c.description));
  return /* @__PURE__ */ f.createElement("div", {
    className: Z(a, {
      [`${a}-drag-in`]: u,
      [`${a}-disabled`]: l
    }, o),
    onDragEnter: h,
    onDragLeave: p,
    onDrop: v,
    "aria-hidden": l,
    style: s
  }, /* @__PURE__ */ f.createElement(rr.Dragger, ve({
    showUploadList: !1
  }, i, {
    ref: e,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), b));
}
const oa = /* @__PURE__ */ f.forwardRef(ia);
function sa(n, e) {
  const {
    prefixCls: t,
    rootClassName: r,
    rootStyle: i,
    className: o,
    style: s,
    items: a,
    children: c,
    getDropContainer: l,
    placeholder: u,
    onChange: d,
    onRemove: h,
    overflow: p,
    imageProps: v,
    disabled: b,
    classNames: g = {},
    styles: m = {},
    ...S
  } = n, {
    getPrefixCls: C,
    direction: y
  } = Ve(), x = C("attachment", t), w = dr("attachments"), {
    classNames: _,
    styles: P
  } = w, O = f.useRef(null), T = f.useRef(null);
  f.useImperativeHandle(e, () => ({
    nativeElement: O.current,
    upload: (F) => {
      var G, Q;
      const J = (Q = (G = T.current) == null ? void 0 : G.nativeElement) == null ? void 0 : Q.querySelector('input[type="file"]');
      if (J) {
        const ae = new DataTransfer();
        ae.items.add(F), J.files = ae.files, J.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [M, I, N] = kr(x), W = Z(I, N), [A, B] = ln([], {
    value: a
  }), $ = _e((F) => {
    B(F.fileList), d == null || d(F);
  }), H = {
    ...S,
    fileList: A,
    onChange: $
  }, E = (F) => Promise.resolve(typeof h == "function" ? h(F) : h).then((J) => {
    if (J === !1)
      return;
    const G = A.filter((Q) => Q.uid !== F.uid);
    $({
      file: {
        ...F,
        status: "removed"
      },
      fileList: G
    });
  });
  let ce;
  const ee = (F, J, G) => {
    const Q = typeof u == "function" ? u(F) : u;
    return /* @__PURE__ */ f.createElement(oa, {
      placeholder: Q,
      upload: H,
      prefixCls: x,
      className: Z(_.placeholder, g.placeholder),
      style: {
        ...P.placeholder,
        ...m.placeholder,
        ...J == null ? void 0 : J.style
      },
      ref: G
    });
  };
  if (c)
    ce = /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement(Dr, {
      upload: H,
      rootClassName: r,
      ref: T
    }, c), /* @__PURE__ */ f.createElement(Wn, {
      getDropContainer: l,
      prefixCls: x,
      className: Z(W, r)
    }, ee("drop")));
  else {
    const F = A.length > 0;
    ce = /* @__PURE__ */ f.createElement("div", {
      className: Z(x, W, {
        [`${x}-rtl`]: y === "rtl"
      }, o, r),
      style: {
        ...i,
        ...s
      },
      dir: y || "ltr",
      ref: O
    }, /* @__PURE__ */ f.createElement(ra, {
      prefixCls: x,
      items: A,
      onRemove: E,
      overflow: p,
      upload: H,
      listClassName: Z(_.list, g.list),
      listStyle: {
        ...P.list,
        ...m.list,
        ...!F && {
          display: "none"
        }
      },
      uploadClassName: Z(_.upload, g.upload),
      uploadStyle: {
        ...P.upload,
        ...m.upload
      },
      itemClassName: Z(_.item, g.item),
      itemStyle: {
        ...P.item,
        ...m.item
      },
      imageProps: v
    }), ee("inline", F ? {
      style: {
        display: "none"
      }
    } : {}, T), /* @__PURE__ */ f.createElement(Wn, {
      getDropContainer: l || (() => O.current),
      prefixCls: x,
      className: W
    }, ee("drop")));
  }
  return M(/* @__PURE__ */ f.createElement(Xe.Provider, {
    value: {
      disabled: b
    }
  }, ce));
}
const Wr = /* @__PURE__ */ f.forwardRef(sa);
Wr.FileCard = Nr;
function aa(n, e) {
  return Kr(n, () => {
    const t = e(), {
      nativeElement: r
    } = t;
    return new Proxy(r, {
      get(i, o) {
        return t[o] ? t[o] : Reflect.get(i, o);
      }
    });
  });
}
const Fr = /* @__PURE__ */ R.createContext({}), Kn = () => ({
  height: 0
}), Yn = (n) => ({
  height: n.scrollHeight
});
function la(n) {
  const {
    title: e,
    onOpenChange: t,
    open: r,
    children: i,
    className: o,
    style: s,
    classNames: a = {},
    styles: c = {},
    closable: l,
    forceRender: u
  } = n, {
    prefixCls: d
  } = R.useContext(Fr), h = `${d}-header`;
  return /* @__PURE__ */ R.createElement($r, {
    motionEnter: !0,
    motionLeave: !0,
    motionName: `${h}-motion`,
    leavedClassName: `${h}-motion-hidden`,
    onEnterStart: Kn,
    onEnterActive: Yn,
    onLeaveStart: Yn,
    onLeaveActive: Kn,
    visible: r,
    forceRender: u
  }, ({
    className: p,
    style: v
  }) => /* @__PURE__ */ R.createElement("div", {
    className: Z(h, p, o),
    style: {
      ...v,
      ...s
    }
  }, (l !== !1 || e) && /* @__PURE__ */ R.createElement("div", {
    className: (
      // We follow antd naming standard here.
      // So the header part is use `-header` suffix.
      // Though its little bit weird for double `-header`.
      Z(`${h}-header`, a.header)
    ),
    style: {
      ...c.header
    }
  }, /* @__PURE__ */ R.createElement("div", {
    className: `${h}-title`
  }, e), l !== !1 && /* @__PURE__ */ R.createElement("div", {
    className: `${h}-close`
  }, /* @__PURE__ */ R.createElement(De, {
    type: "text",
    icon: /* @__PURE__ */ R.createElement(yi, null),
    size: "small",
    onClick: () => {
      t == null || t(!r);
    }
  }))), i && /* @__PURE__ */ R.createElement("div", {
    className: Z(`${h}-content`, a.content),
    style: {
      ...c.content
    }
  }, i)));
}
const Lt = /* @__PURE__ */ R.createContext(null);
function ca(n, e) {
  const {
    className: t,
    action: r,
    onClick: i,
    ...o
  } = n, s = R.useContext(Lt), {
    prefixCls: a,
    disabled: c
  } = s, l = o.disabled ?? c ?? s[`${r}Disabled`];
  return /* @__PURE__ */ R.createElement(De, ve({
    type: "text"
  }, o, {
    ref: e,
    onClick: (u) => {
      var d;
      l || ((d = s[r]) == null || d.call(s), i == null || i(u));
    },
    className: Z(a, t, {
      [`${a}-disabled`]: l
    })
  }));
}
const Ot = /* @__PURE__ */ R.forwardRef(ca);
function ua(n, e) {
  return /* @__PURE__ */ R.createElement(Ot, ve({
    icon: /* @__PURE__ */ R.createElement(wi, null)
  }, n, {
    action: "onClear",
    ref: e
  }));
}
const da = /* @__PURE__ */ R.forwardRef(ua), fa = /* @__PURE__ */ Yr((n) => {
  const {
    className: e
  } = n;
  return /* @__PURE__ */ f.createElement("svg", {
    color: "currentColor",
    viewBox: "0 0 1000 1000",
    xmlns: "http://www.w3.org/2000/svg",
    className: e
  }, /* @__PURE__ */ f.createElement("title", null, "Stop Loading"), /* @__PURE__ */ f.createElement("rect", {
    fill: "currentColor",
    height: "250",
    rx: "24",
    ry: "24",
    width: "250",
    x: "375",
    y: "375"
  }), /* @__PURE__ */ f.createElement("circle", {
    cx: "500",
    cy: "500",
    fill: "none",
    r: "450",
    stroke: "currentColor",
    strokeWidth: "100",
    opacity: "0.45"
  }), /* @__PURE__ */ f.createElement("circle", {
    cx: "500",
    cy: "500",
    fill: "none",
    r: "450",
    stroke: "currentColor",
    strokeWidth: "100",
    strokeDasharray: "600 9999999"
  }, /* @__PURE__ */ f.createElement("animateTransform", {
    attributeName: "transform",
    dur: "1s",
    from: "0 500 500",
    repeatCount: "indefinite",
    to: "360 500 500",
    type: "rotate"
  })));
});
function ha(n, e) {
  const {
    prefixCls: t
  } = R.useContext(Lt), {
    className: r
  } = n;
  return /* @__PURE__ */ R.createElement(Ot, ve({
    icon: null,
    color: "primary",
    variant: "text",
    shape: "circle"
  }, n, {
    className: Z(r, `${t}-loading-button`),
    action: "onCancel",
    ref: e
  }), /* @__PURE__ */ R.createElement(fa, {
    className: `${t}-loading-icon`
  }));
}
const jr = /* @__PURE__ */ R.forwardRef(ha);
function pa(n, e) {
  return /* @__PURE__ */ R.createElement(Ot, ve({
    icon: /* @__PURE__ */ R.createElement(Si, null),
    type: "primary",
    shape: "circle"
  }, n, {
    action: "onSend",
    ref: e
  }));
}
const Br = /* @__PURE__ */ R.forwardRef(pa), Be = 1e3, He = 4, at = 140, Zn = at / 2, tt = 250, Qn = 500, nt = 0.8;
function ma({
  className: n
}) {
  return /* @__PURE__ */ f.createElement("svg", {
    color: "currentColor",
    viewBox: `0 0 ${Be} ${Be}`,
    xmlns: "http://www.w3.org/2000/svg",
    className: n
  }, /* @__PURE__ */ f.createElement("title", null, "Speech Recording"), Array.from({
    length: He
  }).map((e, t) => {
    const r = (Be - at * He) / (He - 1), i = t * (r + at), o = Be / 2 - tt / 2, s = Be / 2 - Qn / 2;
    return /* @__PURE__ */ f.createElement("rect", {
      fill: "currentColor",
      rx: Zn,
      ry: Zn,
      height: tt,
      width: at,
      x: i,
      y: o,
      key: t
    }, /* @__PURE__ */ f.createElement("animate", {
      attributeName: "height",
      values: `${tt}; ${Qn}; ${tt}`,
      keyTimes: "0; 0.5; 1",
      dur: `${nt}s`,
      begin: `${nt / He * t}s`,
      repeatCount: "indefinite"
    }), /* @__PURE__ */ f.createElement("animate", {
      attributeName: "y",
      values: `${o}; ${s}; ${o}`,
      keyTimes: "0; 0.5; 1",
      dur: `${nt}s`,
      begin: `${nt / He * t}s`,
      repeatCount: "indefinite"
    }));
  }));
}
function ga(n, e) {
  const {
    speechRecording: t,
    onSpeechDisabled: r,
    prefixCls: i
  } = R.useContext(Lt);
  let o = null;
  return t ? o = /* @__PURE__ */ R.createElement(ma, {
    className: `${i}-recording-icon`
  }) : r ? o = /* @__PURE__ */ R.createElement(xi, null) : o = /* @__PURE__ */ R.createElement(Ci, null), /* @__PURE__ */ R.createElement(Ot, ve({
    icon: o,
    color: "primary",
    variant: "text"
  }, n, {
    action: "onSpeech",
    ref: e
  }));
}
const Hr = /* @__PURE__ */ R.forwardRef(ga), va = (n) => {
  const {
    componentCls: e,
    calc: t
  } = n, r = `${e}-header`;
  return {
    [e]: {
      [r]: {
        borderBottomWidth: n.lineWidth,
        borderBottomStyle: "solid",
        borderBottomColor: n.colorBorder,
        // ======================== Header ========================
        "&-header": {
          background: n.colorFillAlter,
          fontSize: n.fontSize,
          lineHeight: n.lineHeight,
          paddingBlock: t(n.paddingSM).sub(n.lineWidthBold).equal(),
          paddingInlineStart: n.padding,
          paddingInlineEnd: n.paddingXS,
          display: "flex",
          borderRadius: {
            _skip_check_: !0,
            value: t(n.borderRadius).mul(2).equal()
          },
          borderEndStartRadius: 0,
          borderEndEndRadius: 0,
          [`${r}-title`]: {
            flex: "auto"
          }
        },
        // ======================= Content ========================
        "&-content": {
          padding: n.padding
        },
        // ======================== Motion ========================
        "&-motion": {
          transition: ["height", "border"].map((i) => `${i} ${n.motionDurationSlow}`).join(","),
          overflow: "hidden",
          "&-enter-start, &-leave-active": {
            borderBottomColor: "transparent"
          },
          "&-hidden": {
            display: "none"
          }
        }
      }
    }
  };
}, ba = (n) => {
  const {
    componentCls: e,
    padding: t,
    paddingSM: r,
    paddingXS: i,
    paddingXXS: o,
    lineWidth: s,
    lineWidthBold: a,
    calc: c
  } = n;
  return {
    [e]: {
      position: "relative",
      width: "100%",
      boxSizing: "border-box",
      boxShadow: `${n.boxShadowTertiary}`,
      transition: `background ${n.motionDurationSlow}`,
      // Border
      borderRadius: {
        _skip_check_: !0,
        value: c(n.borderRadius).mul(2).equal()
      },
      borderColor: n.colorBorder,
      borderWidth: 0,
      borderStyle: "solid",
      // Border
      "&:after": {
        content: '""',
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        transition: `border-color ${n.motionDurationSlow}`,
        borderRadius: {
          _skip_check_: !0,
          value: "inherit"
        },
        borderStyle: "inherit",
        borderColor: "inherit",
        borderWidth: s
      },
      // Focus
      "&:focus-within": {
        boxShadow: `${n.boxShadowSecondary}`,
        borderColor: n.colorPrimary,
        "&:after": {
          borderWidth: a
        }
      },
      "&-disabled": {
        background: n.colorBgContainerDisabled
      },
      // ============================== RTL ==============================
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      // ============================ Content ============================
      [`${e}-content`]: {
        display: "flex",
        gap: i,
        width: "100%",
        paddingBlock: r,
        paddingInlineStart: t,
        paddingInlineEnd: r,
        boxSizing: "border-box",
        alignItems: "flex-end"
      },
      // ============================ Prefix =============================
      [`${e}-prefix`]: {
        flex: "none"
      },
      // ============================= Input =============================
      [`${e}-input`]: {
        padding: 0,
        borderRadius: 0,
        flex: "auto",
        alignSelf: "center",
        minHeight: "auto"
      },
      // ============================ Actions ============================
      [`${e}-actions-list`]: {
        flex: "none",
        display: "flex",
        "&-presets": {
          gap: n.paddingXS
        }
      },
      [`${e}-actions-btn`]: {
        "&-disabled": {
          opacity: 0.45
        },
        "&-loading-button": {
          padding: 0,
          border: 0
        },
        "&-loading-icon": {
          height: n.controlHeight,
          width: n.controlHeight,
          verticalAlign: "top"
        },
        "&-recording-icon": {
          height: "1.2em",
          width: "1.2em",
          verticalAlign: "top"
        }
      },
      // ============================ Footer =============================
      [`${e}-footer`]: {
        paddingInlineStart: t,
        paddingInlineEnd: r,
        paddingBlockEnd: r,
        paddingBlockStart: o,
        boxSizing: "border-box"
      }
    }
  };
}, ya = () => ({}), wa = wr("Sender", (n) => {
  const {
    paddingXS: e,
    calc: t
  } = n, r = Mt(n, {
    SenderContentMaxWidth: `calc(100% - ${qt(t(e).add(32).equal())})`
  });
  return [ba(r), va(r)];
}, ya);
let pt;
!pt && typeof window < "u" && (pt = window.SpeechRecognition || window.webkitSpeechRecognition);
function Sa(n, e) {
  const t = _e(n), [r, i, o] = f.useMemo(() => typeof e == "object" ? [e.recording, e.onRecordingChange, typeof e.recording == "boolean"] : [void 0, void 0, !1], [e]), [s, a] = f.useState(null);
  f.useEffect(() => {
    if (typeof navigator < "u" && "permissions" in navigator) {
      let b = null;
      return navigator.permissions.query({
        name: "microphone"
      }).then((g) => {
        a(g.state), g.onchange = function() {
          a(this.state);
        }, b = g;
      }), () => {
        b && (b.onchange = null);
      };
    }
  }, []);
  const c = pt && s !== "denied", l = f.useRef(null), [u, d] = ln(!1, {
    value: r
  }), h = f.useRef(!1), p = () => {
    if (c && !l.current) {
      const b = new pt();
      b.onstart = () => {
        d(!0);
      }, b.onend = () => {
        d(!1);
      }, b.onresult = (g) => {
        var m, S, C;
        if (!h.current) {
          const y = (C = (S = (m = g.results) == null ? void 0 : m[0]) == null ? void 0 : S[0]) == null ? void 0 : C.transcript;
          t(y);
        }
        h.current = !1;
      }, l.current = b;
    }
  }, v = _e((b) => {
    b && !u || (h.current = b, o ? i == null || i(!u) : (p(), l.current && (u ? (l.current.stop(), i == null || i(!1)) : (l.current.start(), i == null || i(!0)))));
  });
  return [c, v, u];
}
function xa(n, e, t) {
  return ns(n, e) || t;
}
const Jn = {
  SendButton: Br,
  ClearButton: da,
  LoadingButton: jr,
  SpeechButton: Hr
}, Ca = /* @__PURE__ */ f.forwardRef((n, e) => {
  const {
    prefixCls: t,
    styles: r = {},
    classNames: i = {},
    className: o,
    rootClassName: s,
    style: a,
    defaultValue: c,
    value: l,
    readOnly: u,
    submitType: d = "enter",
    onSubmit: h,
    loading: p,
    components: v,
    onCancel: b,
    onChange: g,
    actions: m,
    onKeyPress: S,
    onKeyDown: C,
    disabled: y,
    allowSpeech: x,
    prefix: w,
    footer: _,
    header: P,
    onPaste: O,
    onPasteFile: T,
    autoSize: M = {
      maxRows: 8
    },
    ...I
  } = n, {
    direction: N,
    getPrefixCls: W
  } = Ve(), A = W("sender", t), B = f.useRef(null), $ = f.useRef(null);
  aa(e, () => {
    var Y, de;
    return {
      nativeElement: B.current,
      focus: (Y = $.current) == null ? void 0 : Y.focus,
      blur: (de = $.current) == null ? void 0 : de.blur
    };
  });
  const H = dr("sender"), E = `${A}-input`, [ce, ee, F] = wa(A), J = Z(A, H.className, o, s, ee, F, {
    [`${A}-rtl`]: N === "rtl",
    [`${A}-disabled`]: y
  }), G = `${A}-actions-btn`, Q = `${A}-actions-list`, [ae, he] = ln(c || "", {
    value: l
  }), Se = (Y, de) => {
    he(Y), g && g(Y, de);
  }, [z, L, j] = Sa((Y) => {
    Se(`${ae} ${Y}`);
  }, x), te = xa(v, ["input"], Mi.TextArea), ne = {
    ...$o(I, {
      attr: !0,
      aria: !0,
      data: !0
    }),
    ref: $
  }, me = () => {
    ae && h && !p && h(ae);
  }, oe = () => {
    Se("");
  }, U = f.useRef(!1), ge = () => {
    U.current = !0;
  }, ye = () => {
    U.current = !1;
  }, X = (Y) => {
    const de = Y.key === "Enter" && !U.current;
    switch (d) {
      case "enter":
        de && !Y.shiftKey && (Y.preventDefault(), me());
        break;
      case "shiftEnter":
        de && Y.shiftKey && (Y.preventDefault(), me());
        break;
    }
    S == null || S(Y);
  }, re = (Y) => {
    var We;
    const de = (We = Y.clipboardData) == null ? void 0 : We.files;
    de != null && de.length && T && (T(de[0], de), Y.preventDefault()), O == null || O(Y);
  }, ie = (Y) => {
    var de, We;
    Y.target !== ((de = B.current) == null ? void 0 : de.querySelector(`.${E}`)) && Y.preventDefault(), (We = $.current) == null || We.focus();
  };
  let ue = /* @__PURE__ */ f.createElement(ft, {
    className: `${Q}-presets`
  }, x && /* @__PURE__ */ f.createElement(Hr, null), p ? /* @__PURE__ */ f.createElement(jr, null) : /* @__PURE__ */ f.createElement(Br, null));
  typeof m == "function" ? ue = m(ue, {
    components: Jn
  }) : (m || m === !1) && (ue = m);
  const Pe = {
    prefixCls: G,
    onSend: me,
    onSendDisabled: !ae,
    onClear: oe,
    onClearDisabled: !ae,
    onCancel: b,
    onCancelDisabled: !p,
    onSpeech: () => L(!1),
    onSpeechDisabled: !z,
    speechRecording: j,
    disabled: y
  }, Re = typeof _ == "function" ? _({
    components: Jn
  }) : _ || null;
  return ce(/* @__PURE__ */ f.createElement("div", {
    ref: B,
    className: J,
    style: {
      ...H.style,
      ...a
    }
  }, P && /* @__PURE__ */ f.createElement(Fr.Provider, {
    value: {
      prefixCls: A
    }
  }, P), /* @__PURE__ */ f.createElement(Lt.Provider, {
    value: Pe
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${A}-content`,
    onMouseDown: ie
  }, w && /* @__PURE__ */ f.createElement("div", {
    className: Z(`${A}-prefix`, H.classNames.prefix, i.prefix),
    style: {
      ...H.styles.prefix,
      ...r.prefix
    }
  }, w), /* @__PURE__ */ f.createElement(te, ve({}, ne, {
    disabled: y,
    style: {
      ...H.styles.input,
      ...r.input
    },
    className: Z(E, H.classNames.input, i.input),
    autoSize: M,
    value: ae,
    onChange: (Y) => {
      Se(Y.target.value, Y), L(!0);
    },
    onPressEnter: X,
    onCompositionStart: ge,
    onCompositionEnd: ye,
    onKeyDown: C,
    onPaste: re,
    variant: "borderless",
    readOnly: u
  })), ue && /* @__PURE__ */ f.createElement("div", {
    className: Z(Q, H.classNames.actions, i.actions),
    style: {
      ...H.styles.actions,
      ...r.actions
    }
  }, ue)), Re && /* @__PURE__ */ f.createElement("div", {
    className: Z(`${A}-footer`, H.classNames.footer, i.footer),
    style: {
      ...H.styles.footer,
      ...r.footer
    }
  }, Re))));
}), an = Ca;
an.Header = la;
function Ea(n) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(n.trim());
}
function _a(n, e = !1) {
  try {
    if (ni(n))
      return n;
    if (e && !Ea(n))
      return;
    if (typeof n == "string") {
      let t = n.trim();
      return t.startsWith(";") && (t = t.slice(1)), t.endsWith(";") && (t = t.slice(0, -1)), new Function(`return (...args) => (${t})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function er(n, e) {
  return Xt(() => _a(n, e), [n, e]);
}
function lt(n) {
  const e = pe(n);
  return e.current = n, Zr((...t) => {
    var r;
    return (r = e.current) == null ? void 0 : r.call(e, ...t);
  }, []);
}
function Ra({
  value: n,
  onValueChange: e
}) {
  const [t, r] = $e(n), i = pe(e);
  i.current = e;
  const o = pe(t);
  return o.current = t, Ce(() => {
    i.current(t);
  }, [t]), Ce(() => {
    qi(n, o.current) || r(n);
  }, [n]), [t, r];
}
function Ta(n, e) {
  return Object.keys(n).reduce((t, r) => (n[r] !== void 0 && n[r] !== null && (t[r] = n[r]), t), {});
}
function zt(n, e, t, r) {
  return new (t || (t = Promise))(function(i, o) {
    function s(l) {
      try {
        c(r.next(l));
      } catch (u) {
        o(u);
      }
    }
    function a(l) {
      try {
        c(r.throw(l));
      } catch (u) {
        o(u);
      }
    }
    function c(l) {
      var u;
      l.done ? i(l.value) : (u = l.value, u instanceof t ? u : new t(function(d) {
        d(u);
      })).then(s, a);
    }
    c((r = r.apply(n, [])).next());
  });
}
class zr {
  constructor() {
    this.listeners = {};
  }
  on(e, t, r) {
    if (this.listeners[e] || (this.listeners[e] = /* @__PURE__ */ new Set()), this.listeners[e].add(t), r == null ? void 0 : r.once) {
      const i = () => {
        this.un(e, i), this.un(e, t);
      };
      return this.on(e, i), i;
    }
    return () => this.un(e, t);
  }
  un(e, t) {
    var r;
    (r = this.listeners[e]) === null || r === void 0 || r.delete(t);
  }
  once(e, t) {
    return this.on(e, t, {
      once: !0
    });
  }
  unAll() {
    this.listeners = {};
  }
  emit(e, ...t) {
    this.listeners[e] && this.listeners[e].forEach((r) => r(...t));
  }
}
class Pa extends zr {
  constructor(e) {
    super(), this.subscriptions = [], this.isDestroyed = !1, this.options = e;
  }
  onInit() {
  }
  _init(e) {
    this.isDestroyed && (this.subscriptions = [], this.isDestroyed = !1), this.wavesurfer = e, this.onInit();
  }
  destroy() {
    this.emit("destroy"), this.subscriptions.forEach((e) => e()), this.subscriptions = [], this.isDestroyed = !0, this.wavesurfer = void 0;
  }
}
class Ma extends zr {
  constructor() {
    super(...arguments), this.unsubscribe = () => {
    };
  }
  start() {
    this.unsubscribe = this.on("tick", () => {
      requestAnimationFrame(() => {
        this.emit("tick");
      });
    }), this.emit("tick");
  }
  stop() {
    this.unsubscribe();
  }
  destroy() {
    this.unsubscribe();
  }
}
const La = ["audio/webm", "audio/wav", "audio/mpeg", "audio/mp4", "audio/mp3"];
class hn extends Pa {
  constructor(e) {
    var t, r, i, o, s, a;
    super(Object.assign(Object.assign({}, e), {
      audioBitsPerSecond: (t = e.audioBitsPerSecond) !== null && t !== void 0 ? t : 128e3,
      scrollingWaveform: (r = e.scrollingWaveform) !== null && r !== void 0 && r,
      scrollingWaveformWindow: (i = e.scrollingWaveformWindow) !== null && i !== void 0 ? i : 5,
      continuousWaveform: (o = e.continuousWaveform) !== null && o !== void 0 && o,
      renderRecordedAudio: (s = e.renderRecordedAudio) === null || s === void 0 || s,
      mediaRecorderTimeslice: (a = e.mediaRecorderTimeslice) !== null && a !== void 0 ? a : void 0
    })), this.stream = null, this.mediaRecorder = null, this.dataWindow = null, this.isWaveformPaused = !1, this.lastStartTime = 0, this.lastDuration = 0, this.duration = 0, this.timer = new Ma(), this.subscriptions.push(this.timer.on("tick", () => {
      const c = performance.now() - this.lastStartTime;
      this.duration = this.isPaused() ? this.duration : this.lastDuration + c, this.emit("record-progress", this.duration);
    }));
  }
  static create(e) {
    return new hn(e || {});
  }
  renderMicStream(e) {
    var t;
    const r = new AudioContext(), i = r.createMediaStreamSource(e), o = r.createAnalyser();
    i.connect(o), this.options.continuousWaveform && (o.fftSize = 32);
    const s = o.frequencyBinCount, a = new Float32Array(s);
    let c = 0;
    this.wavesurfer && ((t = this.originalOptions) !== null && t !== void 0 || (this.originalOptions = Object.assign({}, this.wavesurfer.options)), this.wavesurfer.options.interact = !1, this.options.scrollingWaveform && (this.wavesurfer.options.cursorWidth = 0));
    const l = setInterval(() => {
      var u, d, h, p;
      if (!this.isWaveformPaused) {
        if (o.getFloatTimeDomainData(a), this.options.scrollingWaveform) {
          const v = Math.floor((this.options.scrollingWaveformWindow || 0) * r.sampleRate), b = Math.min(v, this.dataWindow ? this.dataWindow.length + s : s), g = new Float32Array(v);
          if (this.dataWindow) {
            const m = Math.max(0, v - this.dataWindow.length);
            g.set(this.dataWindow.slice(-b + s), m);
          }
          g.set(a, v - s), this.dataWindow = g;
        } else if (this.options.continuousWaveform) {
          if (!this.dataWindow) {
            const b = this.options.continuousWaveformDuration ? Math.round(100 * this.options.continuousWaveformDuration) : ((d = (u = this.wavesurfer) === null || u === void 0 ? void 0 : u.getWidth()) !== null && d !== void 0 ? d : 0) * window.devicePixelRatio;
            this.dataWindow = new Float32Array(b);
          }
          let v = 0;
          for (let b = 0; b < s; b++) {
            const g = Math.abs(a[b]);
            g > v && (v = g);
          }
          if (c + 1 > this.dataWindow.length) {
            const b = new Float32Array(2 * this.dataWindow.length);
            b.set(this.dataWindow, 0), this.dataWindow = b;
          }
          this.dataWindow[c] = v, c++;
        } else this.dataWindow = a;
        if (this.wavesurfer) {
          const v = ((p = (h = this.dataWindow) === null || h === void 0 ? void 0 : h.length) !== null && p !== void 0 ? p : 0) / 100;
          this.wavesurfer.load("", [this.dataWindow], this.options.scrollingWaveform ? this.options.scrollingWaveformWindow : v).then(() => {
            this.wavesurfer && this.options.continuousWaveform && (this.wavesurfer.setTime(this.getDuration() / 1e3), this.wavesurfer.options.minPxPerSec || this.wavesurfer.setOptions({
              minPxPerSec: this.wavesurfer.getWidth() / this.wavesurfer.getDuration()
            }));
          }).catch((b) => {
            console.error("Error rendering real-time recording data:", b);
          });
        }
      }
    }, 10);
    return {
      onDestroy: () => {
        clearInterval(l), i == null || i.disconnect(), r == null || r.close();
      },
      onEnd: () => {
        this.isWaveformPaused = !0, clearInterval(l), this.stopMic();
      }
    };
  }
  startMic(e) {
    return zt(this, void 0, void 0, function* () {
      let t;
      try {
        t = yield navigator.mediaDevices.getUserMedia({
          audio: e == null || e
        });
      } catch (o) {
        throw new Error("Error accessing the microphone: " + o.message);
      }
      const {
        onDestroy: r,
        onEnd: i
      } = this.renderMicStream(t);
      return this.subscriptions.push(this.once("destroy", r)), this.subscriptions.push(this.once("record-end", i)), this.stream = t, t;
    });
  }
  stopMic() {
    this.stream && (this.stream.getTracks().forEach((e) => e.stop()), this.stream = null, this.mediaRecorder = null);
  }
  startRecording(e) {
    return zt(this, void 0, void 0, function* () {
      const t = this.stream || (yield this.startMic(e));
      this.dataWindow = null;
      const r = this.mediaRecorder || new MediaRecorder(t, {
        mimeType: this.options.mimeType || La.find((s) => MediaRecorder.isTypeSupported(s)),
        audioBitsPerSecond: this.options.audioBitsPerSecond
      });
      this.mediaRecorder = r, this.stopRecording();
      const i = [];
      r.ondataavailable = (s) => {
        s.data.size > 0 && i.push(s.data), this.emit("record-data-available", s.data);
      };
      const o = (s) => {
        var a;
        const c = new Blob(i, {
          type: r.mimeType
        });
        this.emit(s, c), this.options.renderRecordedAudio && (this.applyOriginalOptionsIfNeeded(), (a = this.wavesurfer) === null || a === void 0 || a.load(URL.createObjectURL(c)));
      };
      r.onpause = () => o("record-pause"), r.onstop = () => o("record-end"), r.start(this.options.mediaRecorderTimeslice), this.lastStartTime = performance.now(), this.lastDuration = 0, this.duration = 0, this.isWaveformPaused = !1, this.timer.start(), this.emit("record-start");
    });
  }
  getDuration() {
    return this.duration;
  }
  isRecording() {
    var e;
    return ((e = this.mediaRecorder) === null || e === void 0 ? void 0 : e.state) === "recording";
  }
  isPaused() {
    var e;
    return ((e = this.mediaRecorder) === null || e === void 0 ? void 0 : e.state) === "paused";
  }
  isActive() {
    var e;
    return ((e = this.mediaRecorder) === null || e === void 0 ? void 0 : e.state) !== "inactive";
  }
  stopRecording() {
    var e;
    this.isActive() && ((e = this.mediaRecorder) === null || e === void 0 || e.stop(), this.timer.stop());
  }
  pauseRecording() {
    var e, t;
    this.isRecording() && (this.isWaveformPaused = !0, (e = this.mediaRecorder) === null || e === void 0 || e.requestData(), (t = this.mediaRecorder) === null || t === void 0 || t.pause(), this.timer.stop(), this.lastDuration = this.duration);
  }
  resumeRecording() {
    var e;
    this.isPaused() && (this.isWaveformPaused = !1, (e = this.mediaRecorder) === null || e === void 0 || e.resume(), this.timer.start(), this.lastStartTime = performance.now(), this.emit("record-resume"));
  }
  static getAvailableAudioDevices() {
    return zt(this, void 0, void 0, function* () {
      return navigator.mediaDevices.enumerateDevices().then((e) => e.filter((t) => t.kind === "audioinput"));
    });
  }
  destroy() {
    this.applyOriginalOptionsIfNeeded(), super.destroy(), this.stopRecording(), this.stopMic();
  }
  applyOriginalOptionsIfNeeded() {
    this.wavesurfer && this.originalOptions && (this.wavesurfer.setOptions(this.originalOptions), delete this.originalOptions);
  }
}
class Ge {
  constructor() {
    this.listeners = {};
  }
  /** Subscribe to an event. Returns an unsubscribe function. */
  on(e, t, r) {
    if (this.listeners[e] || (this.listeners[e] = /* @__PURE__ */ new Set()), this.listeners[e].add(t), r != null && r.once) {
      const i = () => {
        this.un(e, i), this.un(e, t);
      };
      return this.on(e, i), i;
    }
    return () => this.un(e, t);
  }
  /** Unsubscribe from an event */
  un(e, t) {
    var r;
    (r = this.listeners[e]) === null || r === void 0 || r.delete(t);
  }
  /** Subscribe to an event only once */
  once(e, t) {
    return this.on(e, t, {
      once: !0
    });
  }
  /** Clear all events */
  unAll() {
    this.listeners = {};
  }
  /** Emit an event */
  emit(e, ...t) {
    this.listeners[e] && this.listeners[e].forEach((r) => r(...t));
  }
}
class Oa extends Ge {
  /** Create a plugin instance */
  constructor(e) {
    super(), this.subscriptions = [], this.isDestroyed = !1, this.options = e;
  }
  /** Called after this.wavesurfer is available */
  onInit() {
  }
  /** Do not call directly, only called by WavesSurfer internally */
  _init(e) {
    this.isDestroyed && (this.subscriptions = [], this.isDestroyed = !1), this.wavesurfer = e, this.onInit();
  }
  /** Destroy the plugin and unsubscribe from all events */
  destroy() {
    this.emit("destroy"), this.subscriptions.forEach((e) => e()), this.subscriptions = [], this.isDestroyed = !0, this.wavesurfer = void 0;
  }
}
var Aa = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
function $a(n, e) {
  return Aa(this, void 0, void 0, function* () {
    const t = new AudioContext({
      sampleRate: e
    });
    return t.decodeAudioData(n).finally(() => t.close());
  });
}
function Da(n) {
  const e = n[0];
  if (e.some((t) => t > 1 || t < -1)) {
    const t = e.length;
    let r = 0;
    for (let i = 0; i < t; i++) {
      const o = Math.abs(e[i]);
      o > r && (r = o);
    }
    for (const i of n)
      for (let o = 0; o < t; o++)
        i[o] /= r;
  }
  return n;
}
function ka(n, e) {
  return typeof n[0] == "number" && (n = [n]), Da(n), {
    duration: e,
    length: n[0].length,
    sampleRate: n[0].length / e,
    numberOfChannels: n.length,
    getChannelData: (t) => n == null ? void 0 : n[t],
    copyFromChannel: AudioBuffer.prototype.copyFromChannel,
    copyToChannel: AudioBuffer.prototype.copyToChannel
  };
}
const rt = {
  decode: $a,
  createBuffer: ka
};
function Vr(n, e) {
  const t = e.xmlns ? document.createElementNS(e.xmlns, n) : document.createElement(n);
  for (const [r, i] of Object.entries(e))
    if (r === "children" && i)
      for (const [o, s] of Object.entries(i))
        s instanceof Node ? t.appendChild(s) : typeof s == "string" ? t.appendChild(document.createTextNode(s)) : t.appendChild(Vr(o, s));
    else r === "style" ? Object.assign(t.style, i) : r === "textContent" ? t.textContent = i : t.setAttribute(r, i.toString());
  return t;
}
function tr(n, e, t) {
  const r = Vr(n, e || {});
  return t == null || t.appendChild(r), r;
}
const Ia = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  createElement: tr,
  default: tr
}, Symbol.toStringTag, {
  value: "Module"
}));
var ct = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
function Na(n, e) {
  return ct(this, void 0, void 0, function* () {
    if (!n.body || !n.headers) return;
    const t = n.body.getReader(), r = Number(n.headers.get("Content-Length")) || 0;
    let i = 0;
    const o = (a) => ct(this, void 0, void 0, function* () {
      i += (a == null ? void 0 : a.length) || 0;
      const c = Math.round(i / r * 100);
      e(c);
    }), s = () => ct(this, void 0, void 0, function* () {
      let a;
      try {
        a = yield t.read();
      } catch {
        return;
      }
      a.done || (o(a.value), yield s());
    });
    s();
  });
}
function Wa(n, e, t) {
  return ct(this, void 0, void 0, function* () {
    const r = yield fetch(n, t);
    if (r.status >= 400)
      throw new Error(`Failed to fetch ${n}: ${r.status} (${r.statusText})`);
    return Na(r.clone(), e), r.blob();
  });
}
const Fa = {
  fetchBlob: Wa
};
var ja = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
class Ba extends Ge {
  constructor(e) {
    super(), this.isExternalMedia = !1, e.media ? (this.media = e.media, this.isExternalMedia = !0) : this.media = document.createElement("audio"), e.mediaControls && (this.media.controls = !0), e.autoplay && (this.media.autoplay = !0), e.playbackRate != null && this.onMediaEvent("canplay", () => {
      e.playbackRate != null && (this.media.playbackRate = e.playbackRate);
    }, {
      once: !0
    });
  }
  onMediaEvent(e, t, r) {
    return this.media.addEventListener(e, t, r), () => this.media.removeEventListener(e, t, r);
  }
  getSrc() {
    return this.media.currentSrc || this.media.src || "";
  }
  revokeSrc() {
    const e = this.getSrc();
    e.startsWith("blob:") && URL.revokeObjectURL(e);
  }
  canPlayType(e) {
    return this.media.canPlayType(e) !== "";
  }
  setSrc(e, t) {
    const r = this.getSrc();
    if (e && r === e) return;
    this.revokeSrc();
    const i = t instanceof Blob && (this.canPlayType(t.type) || !e) ? URL.createObjectURL(t) : e;
    if (r && this.media.removeAttribute("src"), i || e)
      try {
        this.media.src = i;
      } catch {
        this.media.src = e;
      }
  }
  destroy() {
    this.isExternalMedia || (this.media.pause(), this.media.remove(), this.revokeSrc(), this.media.removeAttribute("src"), this.media.load());
  }
  setMediaElement(e) {
    this.media = e;
  }
  /** Start playing the audio */
  play() {
    return ja(this, void 0, void 0, function* () {
      try {
        return yield this.media.play();
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError")
          return;
        throw e;
      }
    });
  }
  /** Pause the audio */
  pause() {
    this.media.pause();
  }
  /** Check if the audio is playing */
  isPlaying() {
    return !this.media.paused && !this.media.ended;
  }
  /** Jump to a specific time in the audio (in seconds) */
  setTime(e) {
    this.media.currentTime = Math.max(0, Math.min(e, this.getDuration()));
  }
  /** Get the duration of the audio in seconds */
  getDuration() {
    return this.media.duration;
  }
  /** Get the current audio position in seconds */
  getCurrentTime() {
    return this.media.currentTime;
  }
  /** Get the audio volume */
  getVolume() {
    return this.media.volume;
  }
  /** Set the audio volume */
  setVolume(e) {
    this.media.volume = e;
  }
  /** Get the audio muted state */
  getMuted() {
    return this.media.muted;
  }
  /** Mute or unmute the audio */
  setMuted(e) {
    this.media.muted = e;
  }
  /** Get the playback speed */
  getPlaybackRate() {
    return this.media.playbackRate;
  }
  /** Check if the audio is seeking */
  isSeeking() {
    return this.media.seeking;
  }
  /** Set the playback speed, pass an optional false to NOT preserve the pitch */
  setPlaybackRate(e, t) {
    t != null && (this.media.preservesPitch = t), this.media.playbackRate = e;
  }
  /** Get the HTML media element */
  getMediaElement() {
    return this.media;
  }
  /** Set a sink id to change the audio output device */
  setSinkId(e) {
    return this.media.setSinkId(e);
  }
}
function Ha(n, e, t, r, i = 3, o = 0, s = 100) {
  if (!n) return () => {
  };
  const a = matchMedia("(pointer: coarse)").matches;
  let c = () => {
  };
  const l = (u) => {
    if (u.button !== o) return;
    u.preventDefault(), u.stopPropagation();
    let d = u.clientX, h = u.clientY, p = !1;
    const v = Date.now(), b = (y) => {
      if (y.preventDefault(), y.stopPropagation(), a && Date.now() - v < s) return;
      const x = y.clientX, w = y.clientY, _ = x - d, P = w - h;
      if (p || Math.abs(_) > i || Math.abs(P) > i) {
        const O = n.getBoundingClientRect(), {
          left: T,
          top: M
        } = O;
        p || (t == null || t(d - T, h - M), p = !0), e(_, P, x - T, w - M), d = x, h = w;
      }
    }, g = (y) => {
      if (p) {
        const x = y.clientX, w = y.clientY, _ = n.getBoundingClientRect(), {
          left: P,
          top: O
        } = _;
        r == null || r(x - P, w - O);
      }
      c();
    }, m = (y) => {
      (!y.relatedTarget || y.relatedTarget === document.documentElement) && g(y);
    }, S = (y) => {
      p && (y.stopPropagation(), y.preventDefault());
    }, C = (y) => {
      p && y.preventDefault();
    };
    document.addEventListener("pointermove", b), document.addEventListener("pointerup", g), document.addEventListener("pointerout", m), document.addEventListener("pointercancel", m), document.addEventListener("touchmove", C, {
      passive: !1
    }), document.addEventListener("click", S, {
      capture: !0
    }), c = () => {
      document.removeEventListener("pointermove", b), document.removeEventListener("pointerup", g), document.removeEventListener("pointerout", m), document.removeEventListener("pointercancel", m), document.removeEventListener("touchmove", C), setTimeout(() => {
        document.removeEventListener("click", S, {
          capture: !0
        });
      }, 10);
    };
  };
  return n.addEventListener("pointerdown", l), () => {
    c(), n.removeEventListener("pointerdown", l);
  };
}
var nr = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
}, za = function(n, e) {
  var t = {};
  for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && e.indexOf(r) < 0 && (t[r] = n[r]);
  if (n != null && typeof Object.getOwnPropertySymbols == "function") for (var i = 0, r = Object.getOwnPropertySymbols(n); i < r.length; i++)
    e.indexOf(r[i]) < 0 && Object.prototype.propertyIsEnumerable.call(n, r[i]) && (t[r[i]] = n[r[i]]);
  return t;
};
class ke extends Ge {
  constructor(e, t) {
    super(), this.timeouts = [], this.isScrollable = !1, this.audioData = null, this.resizeObserver = null, this.lastContainerWidth = 0, this.isDragging = !1, this.subscriptions = [], this.unsubscribeOnScroll = [], this.subscriptions = [], this.options = e;
    const r = this.parentFromOptionsContainer(e.container);
    this.parent = r;
    const [i, o] = this.initHtml();
    r.appendChild(i), this.container = i, this.scrollContainer = o.querySelector(".scroll"), this.wrapper = o.querySelector(".wrapper"), this.canvasWrapper = o.querySelector(".canvases"), this.progressWrapper = o.querySelector(".progress"), this.cursor = o.querySelector(".cursor"), t && o.appendChild(t), this.initEvents();
  }
  parentFromOptionsContainer(e) {
    let t;
    if (typeof e == "string" ? t = document.querySelector(e) : e instanceof HTMLElement && (t = e), !t)
      throw new Error("Container not found");
    return t;
  }
  initEvents() {
    const e = (t) => {
      const r = this.wrapper.getBoundingClientRect(), i = t.clientX - r.left, o = t.clientY - r.top, s = i / r.width, a = o / r.height;
      return [s, a];
    };
    if (this.wrapper.addEventListener("click", (t) => {
      const [r, i] = e(t);
      this.emit("click", r, i);
    }), this.wrapper.addEventListener("dblclick", (t) => {
      const [r, i] = e(t);
      this.emit("dblclick", r, i);
    }), (this.options.dragToSeek === !0 || typeof this.options.dragToSeek == "object") && this.initDrag(), this.scrollContainer.addEventListener("scroll", () => {
      const {
        scrollLeft: t,
        scrollWidth: r,
        clientWidth: i
      } = this.scrollContainer, o = t / r, s = (t + i) / r;
      this.emit("scroll", o, s, t, t + i);
    }), typeof ResizeObserver == "function") {
      const t = this.createDelay(100);
      this.resizeObserver = new ResizeObserver(() => {
        t().then(() => this.onContainerResize()).catch(() => {
        });
      }), this.resizeObserver.observe(this.scrollContainer);
    }
  }
  onContainerResize() {
    const e = this.parent.clientWidth;
    e === this.lastContainerWidth && this.options.height !== "auto" || (this.lastContainerWidth = e, this.reRender());
  }
  initDrag() {
    this.subscriptions.push(Ha(
      this.wrapper,
      // On drag
      (e, t, r) => {
        this.emit("drag", Math.max(0, Math.min(1, r / this.wrapper.getBoundingClientRect().width)));
      },
      // On start drag
      (e) => {
        this.isDragging = !0, this.emit("dragstart", Math.max(0, Math.min(1, e / this.wrapper.getBoundingClientRect().width)));
      },
      // On end drag
      (e) => {
        this.isDragging = !1, this.emit("dragend", Math.max(0, Math.min(1, e / this.wrapper.getBoundingClientRect().width)));
      }
    ));
  }
  getHeight(e, t) {
    var r;
    const o = ((r = this.audioData) === null || r === void 0 ? void 0 : r.numberOfChannels) || 1;
    if (e == null) return 128;
    if (!isNaN(Number(e))) return Number(e);
    if (e === "auto") {
      const s = this.parent.clientHeight || 128;
      return t != null && t.every((a) => !a.overlay) ? s / o : s;
    }
    return 128;
  }
  initHtml() {
    const e = document.createElement("div"), t = e.attachShadow({
      mode: "open"
    }), r = this.options.cspNonce && typeof this.options.cspNonce == "string" ? this.options.cspNonce.replace(/"/g, "") : "";
    return t.innerHTML = `
      <style${r ? ` nonce="${r}"` : ""}>
        :host {
          user-select: none;
          min-width: 1px;
        }
        :host audio {
          display: block;
          width: 100%;
        }
        :host .scroll {
          overflow-x: auto;
          overflow-y: hidden;
          width: 100%;
          position: relative;
        }
        :host .noScrollbar {
          scrollbar-color: transparent;
          scrollbar-width: none;
        }
        :host .noScrollbar::-webkit-scrollbar {
          display: none;
          -webkit-appearance: none;
        }
        :host .wrapper {
          position: relative;
          overflow: visible;
          z-index: 2;
        }
        :host .canvases {
          min-height: ${this.getHeight(this.options.height, this.options.splitChannels)}px;
        }
        :host .canvases > div {
          position: relative;
        }
        :host canvas {
          display: block;
          position: absolute;
          top: 0;
          image-rendering: pixelated;
        }
        :host .progress {
          pointer-events: none;
          position: absolute;
          z-index: 2;
          top: 0;
          left: 0;
          width: 0;
          height: 100%;
          overflow: hidden;
        }
        :host .progress > div {
          position: relative;
        }
        :host .cursor {
          pointer-events: none;
          position: absolute;
          z-index: 5;
          top: 0;
          left: 0;
          height: 100%;
          border-radius: 2px;
        }
      </style>

      <div class="scroll" part="scroll">
        <div class="wrapper" part="wrapper">
          <div class="canvases" part="canvases"></div>
          <div class="progress" part="progress"></div>
          <div class="cursor" part="cursor"></div>
        </div>
      </div>
    `, [e, t];
  }
  /** Wavesurfer itself calls this method. Do not call it manually. */
  setOptions(e) {
    if (this.options.container !== e.container) {
      const t = this.parentFromOptionsContainer(e.container);
      t.appendChild(this.container), this.parent = t;
    }
    (e.dragToSeek === !0 || typeof this.options.dragToSeek == "object") && this.initDrag(), this.options = e, this.reRender();
  }
  getWrapper() {
    return this.wrapper;
  }
  getWidth() {
    return this.scrollContainer.clientWidth;
  }
  getScroll() {
    return this.scrollContainer.scrollLeft;
  }
  setScroll(e) {
    this.scrollContainer.scrollLeft = e;
  }
  setScrollPercentage(e) {
    const {
      scrollWidth: t
    } = this.scrollContainer, r = t * e;
    this.setScroll(r);
  }
  destroy() {
    var e, t;
    this.subscriptions.forEach((r) => r()), this.container.remove(), (e = this.resizeObserver) === null || e === void 0 || e.disconnect(), (t = this.unsubscribeOnScroll) === null || t === void 0 || t.forEach((r) => r()), this.unsubscribeOnScroll = [];
  }
  createDelay(e = 10) {
    let t, r;
    const i = () => {
      t && clearTimeout(t), r && r();
    };
    return this.timeouts.push(i), () => new Promise((o, s) => {
      i(), r = s, t = setTimeout(() => {
        t = void 0, r = void 0, o();
      }, e);
    });
  }
  // Convert array of color values to linear gradient
  convertColorValues(e) {
    if (!Array.isArray(e)) return e || "";
    if (e.length < 2) return e[0] || "";
    const t = document.createElement("canvas"), r = t.getContext("2d"), i = t.height * (window.devicePixelRatio || 1), o = r.createLinearGradient(0, 0, 0, i), s = 1 / (e.length - 1);
    return e.forEach((a, c) => {
      const l = c * s;
      o.addColorStop(l, a);
    }), o;
  }
  getPixelRatio() {
    return Math.max(1, window.devicePixelRatio || 1);
  }
  renderBarWaveform(e, t, r, i) {
    const o = e[0], s = e[1] || e[0], a = o.length, {
      width: c,
      height: l
    } = r.canvas, u = l / 2, d = this.getPixelRatio(), h = t.barWidth ? t.barWidth * d : 1, p = t.barGap ? t.barGap * d : t.barWidth ? h / 2 : 0, v = t.barRadius || 0, b = c / (h + p) / a, g = v && "roundRect" in r ? "roundRect" : "rect";
    r.beginPath();
    let m = 0, S = 0, C = 0;
    for (let y = 0; y <= a; y++) {
      const x = Math.round(y * b);
      if (x > m) {
        const P = Math.round(S * u * i), O = Math.round(C * u * i), T = P + O || 1;
        let M = u - P;
        t.barAlign === "top" ? M = 0 : t.barAlign === "bottom" && (M = l - T), r[g](m * (h + p), M, h, T, v), m = x, S = 0, C = 0;
      }
      const w = Math.abs(o[y] || 0), _ = Math.abs(s[y] || 0);
      w > S && (S = w), _ > C && (C = _);
    }
    r.fill(), r.closePath();
  }
  renderLineWaveform(e, t, r, i) {
    const o = (s) => {
      const a = e[s] || e[0], c = a.length, {
        height: l
      } = r.canvas, u = l / 2, d = r.canvas.width / c;
      r.moveTo(0, u);
      let h = 0, p = 0;
      for (let v = 0; v <= c; v++) {
        const b = Math.round(v * d);
        if (b > h) {
          const m = Math.round(p * u * i) || 1, S = u + m * (s === 0 ? -1 : 1);
          r.lineTo(h, S), h = b, p = 0;
        }
        const g = Math.abs(a[v] || 0);
        g > p && (p = g);
      }
      r.lineTo(h, u);
    };
    r.beginPath(), o(0), o(1), r.fill(), r.closePath();
  }
  renderWaveform(e, t, r) {
    if (r.fillStyle = this.convertColorValues(t.waveColor), t.renderFunction) {
      t.renderFunction(e, r);
      return;
    }
    let i = t.barHeight || 1;
    if (t.normalize) {
      const o = Array.from(e[0]).reduce((s, a) => Math.max(s, Math.abs(a)), 0);
      i = o ? 1 / o : 1;
    }
    if (t.barWidth || t.barGap || t.barAlign) {
      this.renderBarWaveform(e, t, r, i);
      return;
    }
    this.renderLineWaveform(e, t, r, i);
  }
  renderSingleCanvas(e, t, r, i, o, s, a) {
    const c = this.getPixelRatio(), l = document.createElement("canvas");
    l.width = Math.round(r * c), l.height = Math.round(i * c), l.style.width = `${r}px`, l.style.height = `${i}px`, l.style.left = `${Math.round(o)}px`, s.appendChild(l);
    const u = l.getContext("2d");
    if (this.renderWaveform(e, t, u), l.width > 0 && l.height > 0) {
      const d = l.cloneNode(), h = d.getContext("2d");
      h.drawImage(l, 0, 0), h.globalCompositeOperation = "source-in", h.fillStyle = this.convertColorValues(t.progressColor), h.fillRect(0, 0, l.width, l.height), a.appendChild(d);
    }
  }
  renderMultiCanvas(e, t, r, i, o, s) {
    const a = this.getPixelRatio(), {
      clientWidth: c
    } = this.scrollContainer, l = r / a;
    let u = Math.min(ke.MAX_CANVAS_WIDTH, c, l), d = {};
    if (t.barWidth || t.barGap) {
      const m = t.barWidth || 0.5, S = t.barGap || m / 2, C = m + S;
      u % C !== 0 && (u = Math.floor(u / C) * C);
    }
    if (u === 0) return;
    const h = (m) => {
      if (m < 0 || m >= v || d[m]) return;
      d[m] = !0;
      const S = m * u;
      let C = Math.min(l - S, u);
      if (t.barWidth || t.barGap) {
        const x = t.barWidth || 0.5, w = t.barGap || x / 2, _ = x + w;
        C = Math.floor(C / _) * _;
      }
      if (C <= 0) return;
      const y = e.map((x) => {
        const w = Math.floor(S / l * x.length), _ = Math.floor((S + C) / l * x.length);
        return x.slice(w, _);
      });
      this.renderSingleCanvas(y, t, C, i, S, o, s);
    }, p = () => {
      Object.keys(d).length > ke.MAX_NODES && (o.innerHTML = "", s.innerHTML = "", d = {});
    }, v = Math.ceil(l / u);
    if (!this.isScrollable) {
      for (let m = 0; m < v; m++)
        h(m);
      return;
    }
    const b = this.scrollContainer.scrollLeft / l, g = Math.floor(b * v);
    if (h(g - 1), h(g), h(g + 1), v > 1) {
      const m = this.on("scroll", () => {
        const {
          scrollLeft: S
        } = this.scrollContainer, C = Math.floor(S / l * v);
        p(), h(C - 1), h(C), h(C + 1);
      });
      this.unsubscribeOnScroll.push(m);
    }
  }
  renderChannel(e, t, r, i) {
    var {
      overlay: o
    } = t, s = za(t, ["overlay"]);
    const a = document.createElement("div"), c = this.getHeight(s.height, s.splitChannels);
    a.style.height = `${c}px`, o && i > 0 && (a.style.marginTop = `-${c}px`), this.canvasWrapper.style.minHeight = `${c}px`, this.canvasWrapper.appendChild(a);
    const l = a.cloneNode();
    this.progressWrapper.appendChild(l), this.renderMultiCanvas(e, s, r, c, a, l);
  }
  render(e) {
    return nr(this, void 0, void 0, function* () {
      var t;
      this.timeouts.forEach((c) => c()), this.timeouts = [], this.canvasWrapper.innerHTML = "", this.progressWrapper.innerHTML = "", this.options.width != null && (this.scrollContainer.style.width = typeof this.options.width == "number" ? `${this.options.width}px` : this.options.width);
      const r = this.getPixelRatio(), i = this.scrollContainer.clientWidth, o = Math.ceil(e.duration * (this.options.minPxPerSec || 0));
      this.isScrollable = o > i;
      const s = this.options.fillParent && !this.isScrollable, a = (s ? i : o) * r;
      if (this.wrapper.style.width = s ? "100%" : `${o}px`, this.scrollContainer.style.overflowX = this.isScrollable ? "auto" : "hidden", this.scrollContainer.classList.toggle("noScrollbar", !!this.options.hideScrollbar), this.cursor.style.backgroundColor = `${this.options.cursorColor || this.options.progressColor}`, this.cursor.style.width = `${this.options.cursorWidth}px`, this.audioData = e, this.emit("render"), this.options.splitChannels)
        for (let c = 0; c < e.numberOfChannels; c++) {
          const l = Object.assign(Object.assign({}, this.options), (t = this.options.splitChannels) === null || t === void 0 ? void 0 : t[c]);
          this.renderChannel([e.getChannelData(c)], l, a, c);
        }
      else {
        const c = [e.getChannelData(0)];
        e.numberOfChannels > 1 && c.push(e.getChannelData(1)), this.renderChannel(c, this.options, a, 0);
      }
      Promise.resolve().then(() => this.emit("rendered"));
    });
  }
  reRender() {
    if (this.unsubscribeOnScroll.forEach((r) => r()), this.unsubscribeOnScroll = [], !this.audioData) return;
    const {
      scrollWidth: e
    } = this.scrollContainer, {
      right: t
    } = this.progressWrapper.getBoundingClientRect();
    if (this.render(this.audioData), this.isScrollable && e !== this.scrollContainer.scrollWidth) {
      const {
        right: r
      } = this.progressWrapper.getBoundingClientRect();
      let i = r - t;
      i *= 2, i = i < 0 ? Math.floor(i) : Math.ceil(i), i /= 2, this.scrollContainer.scrollLeft += i;
    }
  }
  zoom(e) {
    this.options.minPxPerSec = e, this.reRender();
  }
  scrollIntoView(e, t = !1) {
    const {
      scrollLeft: r,
      scrollWidth: i,
      clientWidth: o
    } = this.scrollContainer, s = e * i, a = r, c = r + o, l = o / 2;
    if (this.isDragging)
      s + 30 > c ? this.scrollContainer.scrollLeft += 30 : s - 30 < a && (this.scrollContainer.scrollLeft -= 30);
    else {
      (s < a || s > c) && (this.scrollContainer.scrollLeft = s - (this.options.autoCenter ? l : 0));
      const u = s - r - l;
      t && this.options.autoCenter && u > 0 && (this.scrollContainer.scrollLeft += Math.min(u, 10));
    }
    {
      const u = this.scrollContainer.scrollLeft, d = u / i, h = (u + o) / i;
      this.emit("scroll", d, h, u, u + o);
    }
  }
  renderProgress(e, t) {
    if (isNaN(e)) return;
    const r = e * 100;
    this.canvasWrapper.style.clipPath = `polygon(${r}% 0%, 100% 0%, 100% 100%, ${r}% 100%)`, this.progressWrapper.style.width = `${r}%`, this.cursor.style.left = `${r}%`, this.cursor.style.transform = this.options.cursorWidth ? `translateX(-${e * this.options.cursorWidth}px)` : "", this.isScrollable && this.options.autoScroll && this.scrollIntoView(e, t);
  }
  exportImage(e, t, r) {
    return nr(this, void 0, void 0, function* () {
      const i = this.canvasWrapper.querySelectorAll("canvas");
      if (!i.length)
        throw new Error("No waveform data");
      if (r === "dataURL") {
        const o = Array.from(i).map((s) => s.toDataURL(e, t));
        return Promise.resolve(o);
      }
      return Promise.all(Array.from(i).map((o) => new Promise((s, a) => {
        o.toBlob((c) => {
          c ? s(c) : a(new Error("Could not export image"));
        }, e, t);
      })));
    });
  }
}
ke.MAX_CANVAS_WIDTH = 8e3;
ke.MAX_NODES = 10;
class Va extends Ge {
  constructor() {
    super(...arguments), this.unsubscribe = () => {
    };
  }
  start() {
    this.unsubscribe = this.on("tick", () => {
      requestAnimationFrame(() => {
        this.emit("tick");
      });
    }), this.emit("tick");
  }
  stop() {
    this.unsubscribe();
  }
  destroy() {
    this.unsubscribe();
  }
}
var Vt = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
class Ut extends Ge {
  constructor(e = new AudioContext()) {
    super(), this.bufferNode = null, this.playStartTime = 0, this.playedDuration = 0, this._muted = !1, this._playbackRate = 1, this._duration = void 0, this.buffer = null, this.currentSrc = "", this.paused = !0, this.crossOrigin = null, this.seeking = !1, this.autoplay = !1, this.addEventListener = this.on, this.removeEventListener = this.un, this.audioContext = e, this.gainNode = this.audioContext.createGain(), this.gainNode.connect(this.audioContext.destination);
  }
  load() {
    return Vt(this, void 0, void 0, function* () {
    });
  }
  get src() {
    return this.currentSrc;
  }
  set src(e) {
    if (this.currentSrc = e, this._duration = void 0, !e) {
      this.buffer = null, this.emit("emptied");
      return;
    }
    fetch(e).then((t) => {
      if (t.status >= 400)
        throw new Error(`Failed to fetch ${e}: ${t.status} (${t.statusText})`);
      return t.arrayBuffer();
    }).then((t) => this.currentSrc !== e ? null : this.audioContext.decodeAudioData(t)).then((t) => {
      this.currentSrc === e && (this.buffer = t, this.emit("loadedmetadata"), this.emit("canplay"), this.autoplay && this.play());
    });
  }
  _play() {
    var e;
    if (!this.paused) return;
    this.paused = !1, (e = this.bufferNode) === null || e === void 0 || e.disconnect(), this.bufferNode = this.audioContext.createBufferSource(), this.buffer && (this.bufferNode.buffer = this.buffer), this.bufferNode.playbackRate.value = this._playbackRate, this.bufferNode.connect(this.gainNode);
    let t = this.playedDuration * this._playbackRate;
    (t >= this.duration || t < 0) && (t = 0, this.playedDuration = 0), this.bufferNode.start(this.audioContext.currentTime, t), this.playStartTime = this.audioContext.currentTime, this.bufferNode.onended = () => {
      this.currentTime >= this.duration && (this.pause(), this.emit("ended"));
    };
  }
  _pause() {
    var e;
    this.paused = !0, (e = this.bufferNode) === null || e === void 0 || e.stop(), this.playedDuration += this.audioContext.currentTime - this.playStartTime;
  }
  play() {
    return Vt(this, void 0, void 0, function* () {
      this.paused && (this._play(), this.emit("play"));
    });
  }
  pause() {
    this.paused || (this._pause(), this.emit("pause"));
  }
  stopAt(e) {
    const t = e - this.currentTime, r = this.bufferNode;
    r == null || r.stop(this.audioContext.currentTime + t), r == null || r.addEventListener("ended", () => {
      r === this.bufferNode && (this.bufferNode = null, this.pause());
    }, {
      once: !0
    });
  }
  setSinkId(e) {
    return Vt(this, void 0, void 0, function* () {
      return this.audioContext.setSinkId(e);
    });
  }
  get playbackRate() {
    return this._playbackRate;
  }
  set playbackRate(e) {
    this._playbackRate = e, this.bufferNode && (this.bufferNode.playbackRate.value = e);
  }
  get currentTime() {
    return (this.paused ? this.playedDuration : this.playedDuration + (this.audioContext.currentTime - this.playStartTime)) * this._playbackRate;
  }
  set currentTime(e) {
    const t = !this.paused;
    t && this._pause(), this.playedDuration = e / this._playbackRate, t && this._play(), this.emit("seeking"), this.emit("timeupdate");
  }
  get duration() {
    var e, t;
    return (e = this._duration) !== null && e !== void 0 ? e : ((t = this.buffer) === null || t === void 0 ? void 0 : t.duration) || 0;
  }
  set duration(e) {
    this._duration = e;
  }
  get volume() {
    return this.gainNode.gain.value;
  }
  set volume(e) {
    this.gainNode.gain.value = e, this.emit("volumechange");
  }
  get muted() {
    return this._muted;
  }
  set muted(e) {
    this._muted !== e && (this._muted = e, this._muted ? this.gainNode.disconnect() : this.gainNode.connect(this.audioContext.destination));
  }
  canPlayType(e) {
    return /^(audio|video)\//.test(e);
  }
  /** Get the GainNode used to play the audio. Can be used to attach filters. */
  getGainNode() {
    return this.gainNode;
  }
  /** Get decoded audio */
  getChannelData() {
    const e = [];
    if (!this.buffer) return e;
    const t = this.buffer.numberOfChannels;
    for (let r = 0; r < t; r++)
      e.push(this.buffer.getChannelData(r));
    return e;
  }
  /**
   * Imitate `HTMLElement.removeAttribute` for compatibility with `Player`.
   */
  removeAttribute(e) {
    switch (e) {
      case "src":
        this.src = "";
        break;
      case "playbackRate":
        this.playbackRate = 0;
        break;
      case "currentTime":
        this.currentTime = 0;
        break;
      case "duration":
        this.duration = 0;
        break;
      case "volume":
        this.volume = 0;
        break;
      case "muted":
        this.muted = !1;
        break;
    }
  }
}
var Me = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
const Ua = {
  waveColor: "#999",
  progressColor: "#555",
  cursorWidth: 1,
  minPxPerSec: 0,
  fillParent: !0,
  interact: !0,
  dragToSeek: !1,
  autoScroll: !0,
  autoCenter: !0,
  sampleRate: 8e3
};
class qe extends Ba {
  /** Create a new WaveSurfer instance */
  static create(e) {
    return new qe(e);
  }
  /** Create a new WaveSurfer instance */
  constructor(e) {
    const t = e.media || (e.backend === "WebAudio" ? new Ut() : void 0);
    super({
      media: t,
      mediaControls: e.mediaControls,
      autoplay: e.autoplay,
      playbackRate: e.audioRate
    }), this.plugins = [], this.decodedData = null, this.stopAtPosition = null, this.subscriptions = [], this.mediaSubscriptions = [], this.abortController = null, this.options = Object.assign({}, Ua, e), this.timer = new Va();
    const r = t ? void 0 : this.getMediaElement();
    this.renderer = new ke(this.options, r), this.initPlayerEvents(), this.initRendererEvents(), this.initTimerEvents(), this.initPlugins();
    const i = this.options.url || this.getSrc() || "";
    Promise.resolve().then(() => {
      this.emit("init");
      const {
        peaks: o,
        duration: s
      } = this.options;
      (i || o && s) && this.load(i, o, s).catch(() => null);
    });
  }
  updateProgress(e = this.getCurrentTime()) {
    return this.renderer.renderProgress(e / this.getDuration(), this.isPlaying()), e;
  }
  initTimerEvents() {
    this.subscriptions.push(this.timer.on("tick", () => {
      if (!this.isSeeking()) {
        const e = this.updateProgress();
        this.emit("timeupdate", e), this.emit("audioprocess", e), this.stopAtPosition != null && this.isPlaying() && e >= this.stopAtPosition && this.pause();
      }
    }));
  }
  initPlayerEvents() {
    this.isPlaying() && (this.emit("play"), this.timer.start()), this.mediaSubscriptions.push(this.onMediaEvent("timeupdate", () => {
      const e = this.updateProgress();
      this.emit("timeupdate", e);
    }), this.onMediaEvent("play", () => {
      this.emit("play"), this.timer.start();
    }), this.onMediaEvent("pause", () => {
      this.emit("pause"), this.timer.stop(), this.stopAtPosition = null;
    }), this.onMediaEvent("emptied", () => {
      this.timer.stop(), this.stopAtPosition = null;
    }), this.onMediaEvent("ended", () => {
      this.emit("timeupdate", this.getDuration()), this.emit("finish"), this.stopAtPosition = null;
    }), this.onMediaEvent("seeking", () => {
      this.emit("seeking", this.getCurrentTime());
    }), this.onMediaEvent("error", () => {
      var e;
      this.emit("error", (e = this.getMediaElement().error) !== null && e !== void 0 ? e : new Error("Media error")), this.stopAtPosition = null;
    }));
  }
  initRendererEvents() {
    this.subscriptions.push(
      // Seek on click
      this.renderer.on("click", (e, t) => {
        this.options.interact && (this.seekTo(e), this.emit("interaction", e * this.getDuration()), this.emit("click", e, t));
      }),
      // Double click
      this.renderer.on("dblclick", (e, t) => {
        this.emit("dblclick", e, t);
      }),
      // Scroll
      this.renderer.on("scroll", (e, t, r, i) => {
        const o = this.getDuration();
        this.emit("scroll", e * o, t * o, r, i);
      }),
      // Redraw
      this.renderer.on("render", () => {
        this.emit("redraw");
      }),
      // RedrawComplete
      this.renderer.on("rendered", () => {
        this.emit("redrawcomplete");
      }),
      // DragStart
      this.renderer.on("dragstart", (e) => {
        this.emit("dragstart", e);
      }),
      // DragEnd
      this.renderer.on("dragend", (e) => {
        this.emit("dragend", e);
      })
    );
    {
      let e;
      this.subscriptions.push(this.renderer.on("drag", (t) => {
        if (!this.options.interact) return;
        this.renderer.renderProgress(t), clearTimeout(e);
        let r;
        this.isPlaying() ? r = 0 : this.options.dragToSeek === !0 ? r = 200 : typeof this.options.dragToSeek == "object" && this.options.dragToSeek !== void 0 && (r = this.options.dragToSeek.debounceTime), e = setTimeout(() => {
          this.seekTo(t);
        }, r), this.emit("interaction", t * this.getDuration()), this.emit("drag", t);
      }));
    }
  }
  initPlugins() {
    var e;
    !((e = this.options.plugins) === null || e === void 0) && e.length && this.options.plugins.forEach((t) => {
      this.registerPlugin(t);
    });
  }
  unsubscribePlayerEvents() {
    this.mediaSubscriptions.forEach((e) => e()), this.mediaSubscriptions = [];
  }
  /** Set new wavesurfer options and re-render it */
  setOptions(e) {
    this.options = Object.assign({}, this.options, e), e.duration && !e.peaks && (this.decodedData = rt.createBuffer(this.exportPeaks(), e.duration)), e.peaks && e.duration && (this.decodedData = rt.createBuffer(e.peaks, e.duration)), this.renderer.setOptions(this.options), e.audioRate && this.setPlaybackRate(e.audioRate), e.mediaControls != null && (this.getMediaElement().controls = e.mediaControls);
  }
  /** Register a wavesurfer.js plugin */
  registerPlugin(e) {
    if (this.plugins.includes(e))
      return e;
    e._init(this), this.plugins.push(e);
    const t = e.once("destroy", () => {
      this.plugins = this.plugins.filter((r) => r !== e), this.subscriptions = this.subscriptions.filter((r) => r !== t);
    });
    return this.subscriptions.push(t), e;
  }
  /** Unregister a wavesurfer.js plugin */
  unregisterPlugin(e) {
    this.plugins = this.plugins.filter((t) => t !== e), e.destroy();
  }
  /** For plugins only: get the waveform wrapper div */
  getWrapper() {
    return this.renderer.getWrapper();
  }
  /** For plugins only: get the scroll container client width */
  getWidth() {
    return this.renderer.getWidth();
  }
  /** Get the current scroll position in pixels */
  getScroll() {
    return this.renderer.getScroll();
  }
  /** Set the current scroll position in pixels */
  setScroll(e) {
    return this.renderer.setScroll(e);
  }
  /** Move the start of the viewing window to a specific time in the audio (in seconds) */
  setScrollTime(e) {
    const t = e / this.getDuration();
    this.renderer.setScrollPercentage(t);
  }
  /** Get all registered plugins */
  getActivePlugins() {
    return this.plugins;
  }
  loadAudio(e, t, r, i) {
    return Me(this, void 0, void 0, function* () {
      var o;
      if (this.emit("load", e), !this.options.media && this.isPlaying() && this.pause(), this.decodedData = null, this.stopAtPosition = null, !t && !r) {
        const a = this.options.fetchParams || {};
        window.AbortController && !a.signal && (this.abortController = new AbortController(), a.signal = (o = this.abortController) === null || o === void 0 ? void 0 : o.signal);
        const c = (u) => this.emit("loading", u);
        t = yield Fa.fetchBlob(e, c, a);
        const l = this.options.blobMimeType;
        l && (t = new Blob([t], {
          type: l
        }));
      }
      this.setSrc(e, t);
      const s = yield new Promise((a) => {
        const c = i || this.getDuration();
        c ? a(c) : this.mediaSubscriptions.push(this.onMediaEvent("loadedmetadata", () => a(this.getDuration()), {
          once: !0
        }));
      });
      if (!e && !t) {
        const a = this.getMediaElement();
        a instanceof Ut && (a.duration = s);
      }
      if (r)
        this.decodedData = rt.createBuffer(r, s || 0);
      else if (t) {
        const a = yield t.arrayBuffer();
        this.decodedData = yield rt.decode(a, this.options.sampleRate);
      }
      this.decodedData && (this.emit("decode", this.getDuration()), this.renderer.render(this.decodedData)), this.emit("ready", this.getDuration());
    });
  }
  /** Load an audio file by URL, with optional pre-decoded audio data */
  load(e, t, r) {
    return Me(this, void 0, void 0, function* () {
      try {
        return yield this.loadAudio(e, void 0, t, r);
      } catch (i) {
        throw this.emit("error", i), i;
      }
    });
  }
  /** Load an audio blob */
  loadBlob(e, t, r) {
    return Me(this, void 0, void 0, function* () {
      try {
        return yield this.loadAudio("", e, t, r);
      } catch (i) {
        throw this.emit("error", i), i;
      }
    });
  }
  /** Zoom the waveform by a given pixels-per-second factor */
  zoom(e) {
    if (!this.decodedData)
      throw new Error("No audio loaded");
    this.renderer.zoom(e), this.emit("zoom", e);
  }
  /** Get the decoded audio data */
  getDecodedData() {
    return this.decodedData;
  }
  /** Get decoded peaks */
  exportPeaks({
    channels: e = 2,
    maxLength: t = 8e3,
    precision: r = 1e4
  } = {}) {
    if (!this.decodedData)
      throw new Error("The audio has not been decoded yet");
    const i = Math.min(e, this.decodedData.numberOfChannels), o = [];
    for (let s = 0; s < i; s++) {
      const a = this.decodedData.getChannelData(s), c = [], l = a.length / t;
      for (let u = 0; u < t; u++) {
        const d = a.slice(Math.floor(u * l), Math.ceil((u + 1) * l));
        let h = 0;
        for (let p = 0; p < d.length; p++) {
          const v = d[p];
          Math.abs(v) > Math.abs(h) && (h = v);
        }
        c.push(Math.round(h * r) / r);
      }
      o.push(c);
    }
    return o;
  }
  /** Get the duration of the audio in seconds */
  getDuration() {
    let e = super.getDuration() || 0;
    return (e === 0 || e === 1 / 0) && this.decodedData && (e = this.decodedData.duration), e;
  }
  /** Toggle if the waveform should react to clicks */
  toggleInteraction(e) {
    this.options.interact = e;
  }
  /** Jump to a specific time in the audio (in seconds) */
  setTime(e) {
    this.stopAtPosition = null, super.setTime(e), this.updateProgress(e), this.emit("timeupdate", e);
  }
  /** Seek to a percentage of audio as [0..1] (0 = beginning, 1 = end) */
  seekTo(e) {
    const t = this.getDuration() * e;
    this.setTime(t);
  }
  /** Start playing the audio */
  play(e, t) {
    const r = Object.create(null, {
      play: {
        get: () => super.play
      }
    });
    return Me(this, void 0, void 0, function* () {
      e != null && this.setTime(e);
      const i = yield r.play.call(this);
      return t != null && (this.media instanceof Ut ? this.media.stopAt(t) : this.stopAtPosition = t), i;
    });
  }
  /** Play or pause the audio */
  playPause() {
    return Me(this, void 0, void 0, function* () {
      return this.isPlaying() ? this.pause() : this.play();
    });
  }
  /** Stop the audio and go to the beginning */
  stop() {
    this.pause(), this.setTime(0);
  }
  /** Skip N or -N seconds from the current position */
  skip(e) {
    this.setTime(this.getCurrentTime() + e);
  }
  /** Empty the waveform */
  empty() {
    this.load("", [[0]], 1e-3);
  }
  /** Set HTML media element */
  setMediaElement(e) {
    this.unsubscribePlayerEvents(), super.setMediaElement(e), this.initPlayerEvents();
  }
  exportImage() {
    return Me(this, arguments, void 0, function* (e = "image/png", t = 1, r = "dataURL") {
      return this.renderer.exportImage(e, t, r);
    });
  }
  /** Unmount wavesurfer */
  destroy() {
    var e;
    this.emit("destroy"), (e = this.abortController) === null || e === void 0 || e.abort(), this.plugins.forEach((t) => t.destroy()), this.subscriptions.forEach((t) => t()), this.unsubscribePlayerEvents(), this.timer.destroy(), this.renderer.destroy(), super.destroy();
  }
}
qe.BasePlugin = Oa;
qe.dom = Ia;
function Xa({
  container: n,
  onStop: e
}) {
  const t = pe(null), [r, i] = $e(!1), o = lt(() => {
    var c;
    (c = t.current) == null || c.startRecording();
  }), s = lt(() => {
    var c;
    (c = t.current) == null || c.stopRecording();
  }), a = lt(e);
  return Ce(() => {
    if (n) {
      const l = qe.create({
        normalize: !1,
        container: n
      }).registerPlugin(hn.create());
      t.current = l, l.on("record-start", () => {
        i(!0);
      }), l.on("record-end", (u) => {
        a(u), i(!1);
      });
    }
  }, [n, a]), {
    recording: r,
    start: o,
    stop: s
  };
}
function Ga(n) {
  const e = function(a, c, l) {
    for (let u = 0; u < l.length; u++)
      a.setUint8(c + u, l.charCodeAt(u));
  }, t = n.numberOfChannels, r = n.length * t * 2 + 44, i = new ArrayBuffer(r), o = new DataView(i);
  let s = 0;
  e(o, s, "RIFF"), s += 4, o.setUint32(s, r - 8, !0), s += 4, e(o, s, "WAVE"), s += 4, e(o, s, "fmt "), s += 4, o.setUint32(s, 16, !0), s += 4, o.setUint16(s, 1, !0), s += 2, o.setUint16(s, t, !0), s += 2, o.setUint32(s, n.sampleRate, !0), s += 4, o.setUint32(s, n.sampleRate * 2 * t, !0), s += 4, o.setUint16(s, t * 2, !0), s += 2, o.setUint16(s, 16, !0), s += 2, e(o, s, "data"), s += 4, o.setUint32(s, n.length * t * 2, !0), s += 4;
  for (let a = 0; a < n.numberOfChannels; a++) {
    const c = n.getChannelData(a);
    for (let l = 0; l < c.length; l++)
      o.setInt16(s, c[l] * 65535, !0), s += 2;
  }
  return new Uint8Array(i);
}
async function qa(n, e, t) {
  const r = await n.arrayBuffer(), o = await new AudioContext().decodeAudioData(r), s = new AudioContext(), a = o.numberOfChannels, c = o.sampleRate;
  let l = o.length, u = 0;
  const d = s.createBuffer(a, l, c);
  for (let h = 0; h < a; h++) {
    const p = o.getChannelData(h), v = d.getChannelData(h);
    for (let b = 0; b < l; b++)
      v[b] = p[u + b];
  }
  return Promise.resolve(Ga(d));
}
const Ka = (n) => !!n.name, ze = (n) => {
  var e;
  return {
    text: (n == null ? void 0 : n.text) || "",
    files: ((e = n == null ? void 0 : n.files) == null ? void 0 : e.map((t) => t.path)) || []
  };
}, Qa = So(({
  onValueChange: n,
  onChange: e,
  onPasteFile: t,
  onUpload: r,
  onSubmit: i,
  onRemove: o,
  onDownload: s,
  onDrop: a,
  onPreview: c,
  upload: l,
  onCancel: u,
  children: d,
  readOnly: h,
  loading: p,
  disabled: v,
  placeholder: b,
  elRef: g,
  slots: m,
  mode: S,
  // setSlotParams,
  uploadConfig: C,
  value: y,
  ...x
}) => {
  const [w, _] = $e(!1), P = si(), O = pe(null), [T, M] = $e(!1), I = er(x.actions, !0), N = er(x.footer, !0), {
    start: W,
    stop: A,
    recording: B
  } = Xa({
    container: O.current,
    async onStop(z) {
      const L = new File([await qa(z)], `${Date.now()}_recording_result.wav`, {
        type: "audio/wav"
      });
      ee(L);
    }
  }), [$, H] = Ra({
    onValueChange: n,
    value: y
  }), E = Xt(() => ri(C), [C]), ce = v || (E == null ? void 0 : E.disabled) || p || h || T, ee = lt(async (z) => {
    try {
      if (ce)
        return;
      M(!0);
      const L = E == null ? void 0 : E.maxCount;
      if (typeof L == "number" && L > 0 && F.length >= L)
        return;
      let j = Array.isArray(z) ? z : [z];
      if (L === 1)
        j = j.slice(0, 1);
      else if (j.length === 0) {
        M(!1);
        return;
      } else if (typeof L == "number") {
        const U = L - F.length;
        j = j.slice(0, U < 0 ? 0 : U);
      }
      const te = F, K = j.map((U) => ({
        ...U,
        size: U.size,
        uid: `${U.name}-${Date.now()}`,
        name: U.name,
        status: "uploading"
      }));
      J((U) => [...L === 1 ? [] : U, ...K]);
      const ne = (await l(j)).filter(Boolean).map((U, ge) => ({
        ...U,
        uid: K[ge].uid
      })), me = L === 1 ? ne : [...te, ...ne];
      r == null || r(ne.map((U) => U.path)), M(!1);
      const oe = {
        ...$,
        files: me
      };
      return e == null || e(ze(oe)), H(oe), ne;
    } catch {
      return M(!1), [];
    }
  }), [F, J] = $e(() => ($ == null ? void 0 : $.files) || []);
  Ce(() => {
    J(($ == null ? void 0 : $.files) || []);
  }, [$ == null ? void 0 : $.files]);
  const G = Xt(() => {
    const z = {};
    return F.map((L) => {
      if (!Ka(L)) {
        const j = L.uid || L.url || L.path;
        return z[j] || (z[j] = 0), z[j]++, {
          ...L,
          name: L.orig_name || L.path,
          uid: L.uid || j + "-" + z[j],
          status: "done"
        };
      }
      return L;
    }) || [];
  }, [F]), Q = (E == null ? void 0 : E.allowUpload) ?? !0, ae = Q ? E == null ? void 0 : E.allowSpeech : !1, he = Q ? E == null ? void 0 : E.allowPasteFile : !1, Se = /* @__PURE__ */ q.jsx(Li, {
    title: E == null ? void 0 : E.uploadButtonTooltip,
    children: /* @__PURE__ */ q.jsx(Oi, {
      count: ((E == null ? void 0 : E.showCount) ?? !0) && !w ? G.length : 0,
      children: /* @__PURE__ */ q.jsx(De, {
        onClick: () => {
          _(!w);
        },
        color: "default",
        variant: "text",
        icon: /* @__PURE__ */ q.jsx(Ei, {})
      })
    })
  });
  return /* @__PURE__ */ q.jsxs(q.Fragment, {
    children: [/* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      ref: O
    }), /* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      children: d
    }), /* @__PURE__ */ q.jsx(an, {
      ...x,
      value: $ == null ? void 0 : $.text,
      ref: g,
      disabled: v,
      readOnly: h,
      allowSpeech: ae ? {
        recording: B,
        onRecordingChange(z) {
          ce || (z ? W() : A());
        }
      } : !1,
      placeholder: b,
      loading: p,
      onSubmit: () => {
        P || i == null || i(ze($));
      },
      onCancel: () => {
        u == null || u();
      },
      onChange: (z) => {
        const L = {
          ...$,
          text: z
        };
        e == null || e(ze(L)), H(L);
      },
      onPasteFile: async (z, L) => {
        if (!(he ?? !0))
          return;
        const j = await ee(Array.from(L));
        j && (t == null || t(j.map((te) => te.path)));
      },
      prefix: /* @__PURE__ */ q.jsxs(q.Fragment, {
        children: [Q && S !== "block" ? Se : null, m.prefix ? /* @__PURE__ */ q.jsx(Fe, {
          slot: m.prefix
        }) : null]
      }),
      actions: S === "block" ? !1 : m.actions ? /* @__PURE__ */ q.jsx(Fe, {
        slot: m.actions
      }) : I || x.actions,
      footer: S === "block" ? ({
        components: z
      }) => {
        const {
          SendButton: L,
          SpeechButton: j,
          LoadingButton: te
        } = z;
        return /* @__PURE__ */ q.jsxs(ft, {
          align: "center",
          justify: "space-between",
          gap: "small",
          className: "ms-gr-pro-multimodal-input-footer",
          children: [/* @__PURE__ */ q.jsxs("div", {
            className: "ms-gr-pro-multimodal-input-footer-extra",
            children: [Q ? Se : null, m.footer ? /* @__PURE__ */ q.jsx(Fe, {
              slot: m.footer
            }) : null]
          }), /* @__PURE__ */ q.jsxs(ft, {
            gap: "small",
            className: "ms-gr-pro-multimodal-input-footer-actions",
            children: [ae ? /* @__PURE__ */ q.jsx(j, {}) : null, p ? /* @__PURE__ */ q.jsx(te, {}) : /* @__PURE__ */ q.jsx(L, {})]
          })]
        });
      } : m.footer ? /* @__PURE__ */ q.jsx(Fe, {
        slot: m.footer
      }) : N || x.footer,
      header: Q ? /* @__PURE__ */ q.jsx(an.Header, {
        title: (E == null ? void 0 : E.title) || "Attachments",
        open: w,
        onOpenChange: _,
        children: /* @__PURE__ */ q.jsx(Wr, {
          ...Ta(ii(E, ["title", "placeholder", "showCount", "buttonTooltip", "allowPasteFile"])),
          imageProps: {
            ...E == null ? void 0 : E.imageProps
          },
          disabled: ce,
          getDropContainer: () => E != null && E.fullscreenDrop ? document.body : null,
          items: G,
          placeholder: (z) => {
            var j, te, K, ne, me, oe, U, ge, ye, X, re, ie;
            const L = z === "drop";
            return {
              title: L ? ((te = (j = E == null ? void 0 : E.placeholder) == null ? void 0 : j.drop) == null ? void 0 : te.title) ?? "Drop file here" : ((ne = (K = E == null ? void 0 : E.placeholder) == null ? void 0 : K.inline) == null ? void 0 : ne.title) ?? "Upload files",
              description: L ? ((oe = (me = E == null ? void 0 : E.placeholder) == null ? void 0 : me.drop) == null ? void 0 : oe.description) ?? void 0 : ((ge = (U = E == null ? void 0 : E.placeholder) == null ? void 0 : U.inline) == null ? void 0 : ge.description) ?? "Click or drag files to this area to upload",
              icon: L ? ((X = (ye = E == null ? void 0 : E.placeholder) == null ? void 0 : ye.drop) == null ? void 0 : X.icon) ?? void 0 : ((ie = (re = E == null ? void 0 : E.placeholder) == null ? void 0 : re.inline) == null ? void 0 : ie.icon) ?? /* @__PURE__ */ q.jsx(_i, {})
            };
          },
          onDownload: s,
          onPreview: c,
          onDrop: a,
          onChange: async (z) => {
            try {
              const L = z.file, j = z.fileList, te = G.findIndex((K) => K.uid === L.uid);
              if (te !== -1) {
                if (ce)
                  return;
                o == null || o(L);
                const K = F.slice();
                K.splice(te, 1);
                const ne = {
                  ...$,
                  files: K
                };
                H(ne), e == null || e(ze(ne));
              } else {
                if (ce)
                  return;
                M(!0);
                let K = j.filter((X) => X.status !== "done");
                const ne = E == null ? void 0 : E.maxCount;
                if (ne === 1)
                  K = K.slice(0, 1);
                else if (K.length === 0) {
                  M(!1);
                  return;
                } else if (typeof ne == "number") {
                  const X = ne - F.length;
                  K = K.slice(0, X < 0 ? 0 : X);
                }
                const me = F, oe = K.map((X) => ({
                  ...X,
                  size: X.size,
                  uid: X.uid,
                  name: X.name,
                  status: "uploading"
                }));
                J((X) => [...ne === 1 ? [] : X, ...oe]);
                const U = (await l(K.map((X) => X.originFileObj))).filter(Boolean).map((X, re) => ({
                  ...X,
                  uid: oe[re].uid
                })), ge = ne === 1 ? U : [...me, ...U];
                r == null || r(U.map((X) => X.path)), M(!1);
                const ye = {
                  ...$,
                  files: ge
                };
                J(ge), n == null || n(ye), e == null || e(ze(ye));
              }
            } catch (L) {
              M(!1), console.error(L);
            }
          },
          customRequest: zi
        })
      }) : m.header ? /* @__PURE__ */ q.jsx(Fe, {
        slot: m.header
      }) : x.header
    })]
  });
});
export {
  Qa as MultimodalInput,
  Qa as default
};
