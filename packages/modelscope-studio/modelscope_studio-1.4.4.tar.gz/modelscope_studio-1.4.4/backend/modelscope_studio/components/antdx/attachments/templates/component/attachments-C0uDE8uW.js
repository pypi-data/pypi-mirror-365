import { i as ur, a as Rt, r as dr, Z as Xe, g as fr, t as pr, s as $e, c as ne, b as mr } from "./Index-DCjXUV3_.js";
const $ = window.ms_globals.React, l = window.ms_globals.React, Je = window.ms_globals.React.useMemo, Ke = window.ms_globals.React.useState, xe = window.ms_globals.React.useEffect, sr = window.ms_globals.React.forwardRef, ye = window.ms_globals.React.useRef, ar = window.ms_globals.React.version, lr = window.ms_globals.React.isValidElement, cr = window.ms_globals.React.useLayoutEffect, Vt = window.ms_globals.ReactDOM, qe = window.ms_globals.ReactDOM.createPortal, gr = window.ms_globals.internalContext.useContextPropsContext, hr = window.ms_globals.internalContext.ContextPropsProvider, vr = window.ms_globals.antd.ConfigProvider, Ze = window.ms_globals.antd.theme, Rn = window.ms_globals.antd.Upload, br = window.ms_globals.antd.Progress, yr = window.ms_globals.antd.Image, mt = window.ms_globals.antd.Button, Sr = window.ms_globals.antd.Flex, gt = window.ms_globals.antd.Typography, wr = window.ms_globals.antdIcons.FileTextFilled, xr = window.ms_globals.antdIcons.CloseCircleFilled, Er = window.ms_globals.antdIcons.FileExcelFilled, Cr = window.ms_globals.antdIcons.FileImageFilled, _r = window.ms_globals.antdIcons.FileMarkdownFilled, Lr = window.ms_globals.antdIcons.FilePdfFilled, Rr = window.ms_globals.antdIcons.FilePptFilled, Ir = window.ms_globals.antdIcons.FileWordFilled, Tr = window.ms_globals.antdIcons.FileZipFilled, Pr = window.ms_globals.antdIcons.PlusOutlined, Mr = window.ms_globals.antdIcons.LeftOutlined, Or = window.ms_globals.antdIcons.RightOutlined, Xt = window.ms_globals.antdCssinjs.unit, ht = window.ms_globals.antdCssinjs.token2CSSVar, Wt = window.ms_globals.antdCssinjs.useStyleRegister, Fr = window.ms_globals.antdCssinjs.useCSSVarRegister, Ar = window.ms_globals.antdCssinjs.createTheme, $r = window.ms_globals.antdCssinjs.useCacheToken;
var kr = /\s/;
function jr(e) {
  for (var t = e.length; t-- && kr.test(e.charAt(t)); )
    ;
  return t;
}
var Dr = /^\s+/;
function Nr(e) {
  return e && e.slice(0, jr(e) + 1).replace(Dr, "");
}
var Gt = NaN, zr = /^[-+]0x[0-9a-f]+$/i, Hr = /^0b[01]+$/i, Ur = /^0o[0-7]+$/i, Br = parseInt;
function Kt(e) {
  if (typeof e == "number")
    return e;
  if (ur(e))
    return Gt;
  if (Rt(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = Rt(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Nr(e);
  var n = Hr.test(e);
  return n || Ur.test(e) ? Br(e.slice(2), n ? 2 : 8) : zr.test(e) ? Gt : +e;
}
function Vr() {
}
var vt = function() {
  return dr.Date.now();
}, Xr = "Expected a function", Wr = Math.max, Gr = Math.min;
function Kr(e, t, n) {
  var o, r, i, s, a, c, u = 0, p = !1, d = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(Xr);
  t = Kt(t) || 0, Rt(n) && (p = !!n.leading, d = "maxWait" in n, i = d ? Wr(Kt(n.maxWait) || 0, t) : i, f = "trailing" in n ? !!n.trailing : f);
  function m(h) {
    var L = o, R = r;
    return o = r = void 0, u = h, s = e.apply(R, L), s;
  }
  function y(h) {
    return u = h, a = setTimeout(v, t), p ? m(h) : s;
  }
  function S(h) {
    var L = h - c, R = h - u, F = t - L;
    return d ? Gr(F, i - R) : F;
  }
  function g(h) {
    var L = h - c, R = h - u;
    return c === void 0 || L >= t || L < 0 || d && R >= i;
  }
  function v() {
    var h = vt();
    if (g(h))
      return x(h);
    a = setTimeout(v, S(h));
  }
  function x(h) {
    return a = void 0, f && o ? m(h) : (o = r = void 0, s);
  }
  function E() {
    a !== void 0 && clearTimeout(a), u = 0, o = c = r = a = void 0;
  }
  function b() {
    return a === void 0 ? s : x(vt());
  }
  function w() {
    var h = vt(), L = g(h);
    if (o = arguments, r = this, c = h, L) {
      if (a === void 0)
        return y(c);
      if (d)
        return clearTimeout(a), a = setTimeout(v, t), m(c);
    }
    return a === void 0 && (a = setTimeout(v, t)), s;
  }
  return w.cancel = E, w.flush = b, w;
}
var In = {
  exports: {}
}, et = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var qr = l, Zr = Symbol.for("react.element"), Qr = Symbol.for("react.fragment"), Yr = Object.prototype.hasOwnProperty, Jr = qr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, eo = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Tn(e, t, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) Yr.call(t, o) && !eo.hasOwnProperty(o) && (r[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) r[o] === void 0 && (r[o] = t[o]);
  return {
    $$typeof: Zr,
    type: e,
    key: i,
    ref: s,
    props: r,
    _owner: Jr.current
  };
}
et.Fragment = Qr;
et.jsx = Tn;
et.jsxs = Tn;
In.exports = et;
var ee = In.exports;
const {
  SvelteComponent: to,
  assign: qt,
  binding_callbacks: Zt,
  check_outros: no,
  children: Pn,
  claim_element: Mn,
  claim_space: ro,
  component_subscribe: Qt,
  compute_slots: oo,
  create_slot: io,
  detach: Le,
  element: On,
  empty: Yt,
  exclude_internal_props: Jt,
  get_all_dirty_from_scope: so,
  get_slot_changes: ao,
  group_outros: lo,
  init: co,
  insert_hydration: We,
  safe_not_equal: uo,
  set_custom_element_data: Fn,
  space: fo,
  transition_in: Ge,
  transition_out: It,
  update_slot_base: po
} = window.__gradio__svelte__internal, {
  beforeUpdate: mo,
  getContext: go,
  onDestroy: ho,
  setContext: vo
} = window.__gradio__svelte__internal;
function en(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), r = io(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = On("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      t = Mn(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = Pn(t);
      r && r.l(s), s.forEach(Le), this.h();
    },
    h() {
      Fn(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      We(i, t, s), r && r.m(t, null), e[9](t), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && po(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? ao(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : so(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (Ge(r, i), n = !0);
    },
    o(i) {
      It(r, i), n = !1;
    },
    d(i) {
      i && Le(t), r && r.d(i), e[9](null);
    }
  };
}
function bo(e) {
  let t, n, o, r, i = (
    /*$$slots*/
    e[4].default && en(e)
  );
  return {
    c() {
      t = On("react-portal-target"), n = fo(), i && i.c(), o = Yt(), this.h();
    },
    l(s) {
      t = Mn(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), Pn(t).forEach(Le), n = ro(s), i && i.l(s), o = Yt(), this.h();
    },
    h() {
      Fn(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      We(s, t, a), e[8](t), We(s, n, a), i && i.m(s, a), We(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && Ge(i, 1)) : (i = en(s), i.c(), Ge(i, 1), i.m(o.parentNode, o)) : i && (lo(), It(i, 1, 1, () => {
        i = null;
      }), no());
    },
    i(s) {
      r || (Ge(i), r = !0);
    },
    o(s) {
      It(i), r = !1;
    },
    d(s) {
      s && (Le(t), Le(n), Le(o)), e[8](null), i && i.d(s);
    }
  };
}
function tn(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function yo(e, t, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = oo(i);
  let {
    svelteInit: c
  } = t;
  const u = Xe(tn(t)), p = Xe();
  Qt(e, p, (b) => n(0, o = b));
  const d = Xe();
  Qt(e, d, (b) => n(1, r = b));
  const f = [], m = go("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: S,
    subSlotIndex: g
  } = fr() || {}, v = c({
    parent: m,
    props: u,
    target: p,
    slot: d,
    slotKey: y,
    slotIndex: S,
    subSlotIndex: g,
    onDestroy(b) {
      f.push(b);
    }
  });
  vo("$$ms-gr-react-wrapper", v), mo(() => {
    u.set(tn(t));
  }), ho(() => {
    f.forEach((b) => b());
  });
  function x(b) {
    Zt[b ? "unshift" : "push"](() => {
      o = b, p.set(o);
    });
  }
  function E(b) {
    Zt[b ? "unshift" : "push"](() => {
      r = b, d.set(r);
    });
  }
  return e.$$set = (b) => {
    n(17, t = qt(qt({}, t), Jt(b))), "svelteInit" in b && n(5, c = b.svelteInit), "$$scope" in b && n(6, s = b.$$scope);
  }, t = Jt(t), [o, r, p, d, a, c, s, i, x, E];
}
class So extends to {
  constructor(t) {
    super(), co(this, t, yo, bo, uo, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ms
} = window.__gradio__svelte__internal, nn = window.ms_globals.rerender, bt = window.ms_globals.tree;
function wo(e, t = {}) {
  function n(o) {
    const r = Xe(), i = new So({
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
          }, c = s.parent ?? bt;
          return c.nodes = [...c.nodes, a], nn({
            createPortal: qe,
            node: bt
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== r), nn({
              createPortal: qe,
              node: bt
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
function xo(e) {
  const [t, n] = Ke(() => $e(e));
  return xe(() => {
    let o = !0;
    return e.subscribe((i) => {
      o && (o = !1, i === t) || n(i);
    });
  }, [e]), t;
}
function Eo(e) {
  const t = Je(() => pr(e, (n) => n), [e]);
  return xo(t);
}
const Co = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function _o(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = Lo(n, o), t;
  }, {}) : {};
}
function Lo(e, t) {
  return typeof t == "number" && !Co.includes(e) ? t + "px" : t;
}
function Tt(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const r = l.Children.toArray(e._reactElement.props.children).map((i) => {
      if (l.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Tt(i.props.el);
        return l.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...l.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(qe(l.cloneElement(e._reactElement, {
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
      } = Tt(i);
      t.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Ro(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const ke = sr(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = ye(), [a, c] = Ke([]), {
    forceClone: u
  } = gr(), p = u ? !0 : t;
  return xe(() => {
    var S;
    if (!s.current || !e)
      return;
    let d = e;
    function f() {
      let g = d;
      if (d.tagName.toLowerCase() === "svelte-slot" && d.children.length === 1 && d.children[0] && (g = d.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Ro(i, g), n && g.classList.add(...n.split(" ")), o) {
        const v = _o(o);
        Object.keys(v).forEach((x) => {
          g.style[x] = v[x];
        });
      }
    }
    let m = null, y = null;
    if (p && window.MutationObserver) {
      let g = function() {
        var b, w, h;
        (b = s.current) != null && b.contains(d) && ((w = s.current) == null || w.removeChild(d));
        const {
          portals: x,
          clonedElement: E
        } = Tt(e);
        d = E, c(x), d.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          f();
        }, 50), (h = s.current) == null || h.appendChild(d);
      };
      g();
      const v = Kr(() => {
        g(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      m = new window.MutationObserver(v), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      d.style.display = "contents", f(), (S = s.current) == null || S.appendChild(d);
    return () => {
      var g, v;
      d.style.display = "", (g = s.current) != null && g.contains(d) && ((v = s.current) == null || v.removeChild(d)), m == null || m.disconnect();
    };
  }, [e, p, n, o, i, r, u]), l.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Io = "1.5.0";
function Te() {
  return Te = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (e[o] = n[o]);
    }
    return e;
  }, Te.apply(null, arguments);
}
function Z(e) {
  "@babel/helpers - typeof";
  return Z = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, Z(e);
}
function To(e, t) {
  if (Z(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(e, t);
    if (Z(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function An(e) {
  var t = To(e, "string");
  return Z(t) == "symbol" ? t : t + "";
}
function T(e, t, n) {
  return (t = An(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function rn(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(e, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function I(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? rn(Object(n), !0).forEach(function(o) {
      T(e, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : rn(Object(n)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return e;
}
const Po = /* @__PURE__ */ l.createContext({}), Mo = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Oo = (e) => {
  const t = l.useContext(Po);
  return l.useMemo(() => ({
    ...Mo,
    ...t[e]
  }), [t[e]]);
};
function Qe() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = l.useContext(vr.ConfigContext);
  return {
    theme: r,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o
  };
}
function Fo(e) {
  if (Array.isArray(e)) return e;
}
function Ao(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], c = !0, u = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        c = !1;
      } else for (; !(c = (o = i.call(n)).done) && (a.push(o.value), a.length !== t); c = !0) ;
    } catch (p) {
      u = !0, r = p;
    } finally {
      try {
        if (!c && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (u) throw r;
      }
    }
    return a;
  }
}
function on(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, o = Array(t); n < t; n++) o[n] = e[n];
  return o;
}
function $o(e, t) {
  if (e) {
    if (typeof e == "string") return on(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? on(e, t) : void 0;
  }
}
function ko() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function J(e, t) {
  return Fo(e) || Ao(e, t) || $o(e, t) || ko();
}
function Me(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function sn(e, t) {
  for (var n = 0; n < t.length; n++) {
    var o = t[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, An(o.key), o);
  }
}
function Oe(e, t, n) {
  return t && sn(e.prototype, t), n && sn(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function Ee(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function Pt(e, t) {
  return Pt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Pt(e, t);
}
function tt(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && Pt(e, t);
}
function Ye(e) {
  return Ye = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, Ye(e);
}
function $n() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return ($n = function() {
    return !!e;
  })();
}
function jo(e, t) {
  if (t && (Z(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Ee(e);
}
function nt(e) {
  var t = $n();
  return function() {
    var n, o = Ye(e);
    if (t) {
      var r = Ye(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return jo(this, n);
  };
}
var kn = /* @__PURE__ */ Oe(function e() {
  Me(this, e);
}), jn = "CALC_UNIT", Do = new RegExp(jn, "g");
function yt(e) {
  return typeof e == "number" ? "".concat(e).concat(jn) : e;
}
var No = /* @__PURE__ */ function(e) {
  tt(n, e);
  var t = nt(n);
  function n(o, r) {
    var i;
    Me(this, n), i = t.call(this), T(Ee(i), "result", ""), T(Ee(i), "unitlessCssVar", void 0), T(Ee(i), "lowPriority", void 0);
    var s = Z(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = yt(o) : s === "string" && (i.result = o), i;
  }
  return Oe(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(yt(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(yt(r))), this.lowPriority = !0, this;
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
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(u) {
        return i.result.includes(u);
      }) && (c = !1), this.result = this.result.replace(Do, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(kn), zo = /* @__PURE__ */ function(e) {
  tt(n, e);
  var t = nt(n);
  function n(o) {
    var r;
    return Me(this, n), r = t.call(this), T(Ee(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return Oe(n, [{
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
}(kn), Ho = function(t, n) {
  var o = t === "css" ? No : zo;
  return function(r) {
    return new o(r, n);
  };
}, an = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function Pe(e) {
  var t = $.useRef();
  t.current = e;
  var n = $.useCallback(function() {
    for (var o, r = arguments.length, i = new Array(r), s = 0; s < r; s++)
      i[s] = arguments[s];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return n;
}
function rt() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var ln = rt() ? $.useLayoutEffect : $.useEffect, Uo = function(t, n) {
  var o = $.useRef(!0);
  ln(function() {
    return t(o.current);
  }, n), ln(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, cn = function(t, n) {
  Uo(function(o) {
    if (!o)
      return t();
  }, n);
};
function je(e) {
  var t = $.useRef(!1), n = $.useState(e), o = J(n, 2), r = o[0], i = o[1];
  $.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, c) {
    c && t.current || i(a);
  }
  return [r, s];
}
function St(e) {
  return e !== void 0;
}
function Bo(e, t) {
  var n = t || {}, o = n.defaultValue, r = n.value, i = n.onChange, s = n.postState, a = je(function() {
    return St(r) ? r : St(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), c = J(a, 2), u = c[0], p = c[1], d = r !== void 0 ? r : u, f = s ? s(d) : d, m = Pe(i), y = je([d]), S = J(y, 2), g = S[0], v = S[1];
  cn(function() {
    var E = g[0];
    u !== E && m(u, E);
  }, [g]), cn(function() {
    St(r) || p(r);
  }, [r]);
  var x = Pe(function(E, b) {
    p(E, b), v([d], b);
  });
  return [f, x];
}
var Dn = {
  exports: {}
}, k = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Nt = Symbol.for("react.element"), zt = Symbol.for("react.portal"), ot = Symbol.for("react.fragment"), it = Symbol.for("react.strict_mode"), st = Symbol.for("react.profiler"), at = Symbol.for("react.provider"), lt = Symbol.for("react.context"), Vo = Symbol.for("react.server_context"), ct = Symbol.for("react.forward_ref"), ut = Symbol.for("react.suspense"), dt = Symbol.for("react.suspense_list"), ft = Symbol.for("react.memo"), pt = Symbol.for("react.lazy"), Xo = Symbol.for("react.offscreen"), Nn;
Nn = Symbol.for("react.module.reference");
function se(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Nt:
        switch (e = e.type, e) {
          case ot:
          case st:
          case it:
          case ut:
          case dt:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Vo:
              case lt:
              case ct:
              case pt:
              case ft:
              case at:
                return e;
              default:
                return t;
            }
        }
      case zt:
        return t;
    }
  }
}
k.ContextConsumer = lt;
k.ContextProvider = at;
k.Element = Nt;
k.ForwardRef = ct;
k.Fragment = ot;
k.Lazy = pt;
k.Memo = ft;
k.Portal = zt;
k.Profiler = st;
k.StrictMode = it;
k.Suspense = ut;
k.SuspenseList = dt;
k.isAsyncMode = function() {
  return !1;
};
k.isConcurrentMode = function() {
  return !1;
};
k.isContextConsumer = function(e) {
  return se(e) === lt;
};
k.isContextProvider = function(e) {
  return se(e) === at;
};
k.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Nt;
};
k.isForwardRef = function(e) {
  return se(e) === ct;
};
k.isFragment = function(e) {
  return se(e) === ot;
};
k.isLazy = function(e) {
  return se(e) === pt;
};
k.isMemo = function(e) {
  return se(e) === ft;
};
k.isPortal = function(e) {
  return se(e) === zt;
};
k.isProfiler = function(e) {
  return se(e) === st;
};
k.isStrictMode = function(e) {
  return se(e) === it;
};
k.isSuspense = function(e) {
  return se(e) === ut;
};
k.isSuspenseList = function(e) {
  return se(e) === dt;
};
k.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === ot || e === st || e === it || e === ut || e === dt || e === Xo || typeof e == "object" && e !== null && (e.$$typeof === pt || e.$$typeof === ft || e.$$typeof === at || e.$$typeof === lt || e.$$typeof === ct || e.$$typeof === Nn || e.getModuleId !== void 0);
};
k.typeOf = se;
Dn.exports = k;
var wt = Dn.exports, Wo = Symbol.for("react.element"), Go = Symbol.for("react.transitional.element"), Ko = Symbol.for("react.fragment");
function qo(e) {
  return (
    // Base object type
    e && Z(e) === "object" && // React Element type
    (e.$$typeof === Wo || e.$$typeof === Go) && // React Fragment type
    e.type === Ko
  );
}
var Zo = Number(ar.split(".")[0]), Qo = function(t, n) {
  typeof t == "function" ? t(n) : Z(t) === "object" && t && "current" in t && (t.current = n);
}, Yo = function(t) {
  var n, o;
  if (!t)
    return !1;
  if (zn(t) && Zo >= 19)
    return !0;
  var r = wt.isMemo(t) ? t.type.type : t.type;
  return !(typeof r == "function" && !((n = r.prototype) !== null && n !== void 0 && n.render) && r.$$typeof !== wt.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== wt.ForwardRef);
};
function zn(e) {
  return /* @__PURE__ */ lr(e) && !qo(e);
}
var Jo = function(t) {
  if (t && zn(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function un(e, t, n, o) {
  var r = I({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var c = J(a, 2), u = c[0], p = c[1];
      if (r != null && r[u] || r != null && r[p]) {
        var d;
        (d = r[p]) !== null && d !== void 0 || (r[p] = r == null ? void 0 : r[u]);
      }
    });
  }
  var s = I(I({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Hn = typeof CSSINJS_STATISTIC < "u", Mt = !0;
function Ht() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Hn)
    return Object.assign.apply(Object, [{}].concat(t));
  Mt = !1;
  var o = {};
  return t.forEach(function(r) {
    if (Z(r) === "object") {
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
  }), Mt = !0, o;
}
var dn = {};
function ei() {
}
var ti = function(t) {
  var n, o = t, r = ei;
  return Hn && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (Mt) {
        var c;
        (c = n) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var c;
    dn[s] = {
      global: Array.from(n),
      component: I(I({}, (c = dn[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function fn(e, t, n) {
  if (typeof n == "function") {
    var o;
    return n(Ht(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function ni(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return Xt(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return Xt(i);
      }).join(","), ")");
    }
  };
}
var ri = 1e3 * 60 * 10, oi = /* @__PURE__ */ function() {
  function e() {
    Me(this, e), T(this, "map", /* @__PURE__ */ new Map()), T(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), T(this, "nextID", 0), T(this, "lastAccessBeat", /* @__PURE__ */ new Map()), T(this, "accessBeat", 0);
  }
  return Oe(e, [{
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
        return i && Z(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(Z(i), "_").concat(i);
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
          o - r > ri && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), pn = new oi();
function ii(e, t) {
  return l.useMemo(function() {
    var n = pn.get(t);
    if (n)
      return n;
    var o = e();
    return pn.set(t, o), o;
  }, t);
}
var si = function() {
  return {};
};
function ai(e) {
  var t = e.useCSP, n = t === void 0 ? si : t, o = e.useToken, r = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function c(f, m, y, S) {
    var g = Array.isArray(f) ? f[0] : f;
    function v(R) {
      return "".concat(String(g)).concat(R.slice(0, 1).toUpperCase()).concat(R.slice(1));
    }
    var x = (S == null ? void 0 : S.unitless) || {}, E = typeof a == "function" ? a(f) : {}, b = I(I({}, E), {}, T({}, v("zIndexPopup"), !0));
    Object.keys(x).forEach(function(R) {
      b[v(R)] = x[R];
    });
    var w = I(I({}, S), {}, {
      unitless: b,
      prefixToken: v
    }), h = p(f, m, y, w), L = u(g, y, w);
    return function(R) {
      var F = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : R, C = h(R, F), M = J(C, 2), _ = M[1], O = L(F), P = J(O, 2), A = P[0], D = P[1];
      return [A, _, D];
    };
  }
  function u(f, m, y) {
    var S = y.unitless, g = y.injectStyle, v = g === void 0 ? !0 : g, x = y.prefixToken, E = y.ignore, b = function(L) {
      var R = L.rootCls, F = L.cssVar, C = F === void 0 ? {} : F, M = o(), _ = M.realToken;
      return Fr({
        path: [f],
        prefix: C.prefix,
        key: C.key,
        unitless: S,
        ignore: E,
        token: _,
        scope: R
      }, function() {
        var O = fn(f, _, m), P = un(f, _, O, {
          deprecatedTokens: y == null ? void 0 : y.deprecatedTokens
        });
        return Object.keys(O).forEach(function(A) {
          P[x(A)] = P[A], delete P[A];
        }), P;
      }), null;
    }, w = function(L) {
      var R = o(), F = R.cssVar;
      return [function(C) {
        return v && F ? /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(b, {
          rootCls: L,
          cssVar: F,
          component: f
        }), C) : C;
      }, F == null ? void 0 : F.key];
    };
    return w;
  }
  function p(f, m, y) {
    var S = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(f) ? f : [f, f], v = J(g, 1), x = v[0], E = g.join("-"), b = e.layer || {
      name: "antd"
    };
    return function(w) {
      var h = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : w, L = o(), R = L.theme, F = L.realToken, C = L.hashId, M = L.token, _ = L.cssVar, O = r(), P = O.rootPrefixCls, A = O.iconPrefixCls, D = n(), U = _ ? "css" : "js", W = ii(function() {
        var H = /* @__PURE__ */ new Set();
        return _ && Object.keys(S.unitless || {}).forEach(function(Q) {
          H.add(ht(Q, _.prefix)), H.add(ht(Q, an(x, _.prefix)));
        }), Ho(U, H);
      }, [U, x, _ == null ? void 0 : _.prefix]), ge = ni(U), ce = ge.max, V = ge.min, N = {
        theme: R,
        token: M,
        hashId: C,
        nonce: function() {
          return D.nonce;
        },
        clientOnly: S.clientOnly,
        layer: b,
        // antd is always at top of styles
        order: S.order || -999
      };
      typeof i == "function" && Wt(I(I({}, N), {}, {
        clientOnly: !1,
        path: ["Shared", P]
      }), function() {
        return i(M, {
          prefix: {
            rootPrefixCls: P,
            iconPrefixCls: A
          },
          csp: D
        });
      });
      var G = Wt(I(I({}, N), {}, {
        path: [E, w, A]
      }), function() {
        if (S.injectStyle === !1)
          return [];
        var H = ti(M), Q = H.token, pe = H.flush, ae = fn(x, F, y), Fe = ".".concat(w), me = un(x, F, ae, {
          deprecatedTokens: S.deprecatedTokens
        });
        _ && ae && Z(ae) === "object" && Object.keys(ae).forEach(function(Se) {
          ae[Se] = "var(".concat(ht(Se, an(x, _.prefix)), ")");
        });
        var ue = Ht(Q, {
          componentCls: Fe,
          prefixCls: w,
          iconCls: ".".concat(A),
          antCls: ".".concat(P),
          calc: W,
          // @ts-ignore
          max: ce,
          // @ts-ignore
          min: V
        }, _ ? ae : me), he = m(ue, {
          hashId: C,
          prefixCls: w,
          rootPrefixCls: P,
          iconPrefixCls: A
        });
        pe(x, me);
        var de = typeof s == "function" ? s(ue, w, h, S.resetFont) : null;
        return [S.resetStyle === !1 ? null : de, he];
      });
      return [G, C];
    };
  }
  function d(f, m, y) {
    var S = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = p(f, m, y, I({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, S)), v = function(E) {
      var b = E.prefixCls, w = E.rootCls, h = w === void 0 ? b : w;
      return g(b, h), null;
    };
    return v;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: d,
    genComponentStyleHook: p
  };
}
const li = {
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
}, ci = Object.assign(Object.assign({}, li), {
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
}), X = Math.round;
function xt(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = t(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const mn = (e, t, n) => n === 0 ? e : e / 100;
function Ae(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class fe {
  constructor(t) {
    T(this, "isValid", !0), T(this, "r", 0), T(this, "g", 0), T(this, "b", 0), T(this, "a", 1), T(this, "_h", void 0), T(this, "_s", void 0), T(this, "_l", void 0), T(this, "_v", void 0), T(this, "_max", void 0), T(this, "_min", void 0), T(this, "_brightness", void 0);
    function n(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (t instanceof fe)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = Ae(t.r), this.g = Ae(t.g), this.b = Ae(t.b), this.a = typeof t.a == "number" ? Ae(t.a, 1) : 1;
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
      t === 0 ? this._h = 0 : this._h = X(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
      r: X(i("r")),
      g: X(i("g")),
      b: X(i("b")),
      a: X(i("a") * 100) / 100
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
    const n = this._c(t), o = this.a + n.a * (1 - this.a), r = (i) => X((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
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
      const i = X(this.a * 255).toString(16);
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
    const t = this.getHue(), n = X(this.getSaturation() * 100), o = X(this.getLightness() * 100);
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
    return r[t] = Ae(n, o), r;
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
      const f = X(o * 255);
      this.r = f, this.g = f, this.b = f;
    }
    let i = 0, s = 0, a = 0;
    const c = t / 60, u = (1 - Math.abs(2 * o - 1)) * n, p = u * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = u, s = p) : c >= 1 && c < 2 ? (i = p, s = u) : c >= 2 && c < 3 ? (s = u, a = p) : c >= 3 && c < 4 ? (s = p, a = u) : c >= 4 && c < 5 ? (i = p, a = u) : c >= 5 && c < 6 && (i = u, a = p);
    const d = o - u / 2;
    this.r = X((i + d) * 255), this.g = X((s + d) * 255), this.b = X((a + d) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: o,
    a: r
  }) {
    this._h = t % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = X(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = t / 60, a = Math.floor(s), c = s - a, u = X(o * (1 - n) * 255), p = X(o * (1 - n * c) * 255), d = X(o * (1 - n * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = d, this.b = u;
        break;
      case 1:
        this.r = p, this.b = u;
        break;
      case 2:
        this.r = u, this.b = d;
        break;
      case 3:
        this.r = u, this.g = p;
        break;
      case 4:
        this.r = d, this.g = u;
        break;
      case 5:
      default:
        this.g = u, this.b = p;
        break;
    }
  }
  fromHsvString(t) {
    const n = xt(t, mn);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = xt(t, mn);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = xt(t, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? X(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Et(e) {
  return e >= 0 && e <= 255;
}
function Ne(e, t) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new fe(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: c
  } = new fe(t).toRgb();
  for (let u = 0.01; u <= 1; u += 0.01) {
    const p = Math.round((n - s * (1 - u)) / u), d = Math.round((o - a * (1 - u)) / u), f = Math.round((r - c * (1 - u)) / u);
    if (Et(p) && Et(d) && Et(f))
      return new fe({
        r: p,
        g: d,
        b: f,
        a: Math.round(u * 100) / 100
      }).toRgbString();
  }
  return new fe({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var ui = function(e, t) {
  var n = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (n[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(e); r < o.length; r++)
    t.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[r]) && (n[o[r]] = e[o[r]]);
  return n;
};
function di(e) {
  const {
    override: t
  } = e, n = ui(e, ["override"]), o = Object.assign({}, t);
  Object.keys(ci).forEach((f) => {
    delete o[f];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, c = 992, u = 1200, p = 1600;
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
    colorSplit: Ne(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: Ne(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: Ne(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: Ne(r.colorPrimaryBg, r.colorBgContainer),
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
    screenLGMax: u - 1,
    screenXL: u,
    screenXLMin: u,
    screenXLMax: p - 1,
    screenXXL: p,
    screenXXLMin: p,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new fe("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new fe("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new fe("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const fi = {
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
}, pi = {
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
}, mi = Ar(Ze.defaultAlgorithm), gi = {
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
}, Un = (e, t, n) => {
  const o = n.getDerivativeToken(e), {
    override: r,
    ...i
  } = t;
  let s = {
    ...o,
    override: r
  };
  return s = di(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: u,
      ...p
    } = c;
    let d = p;
    u && (d = Un({
      ...s,
      ...p
    }, {
      override: p
    }, u)), s[a] = d;
  }), s;
};
function hi() {
  const {
    token: e,
    hashed: t,
    theme: n = mi,
    override: o,
    cssVar: r
  } = l.useContext(Ze._internalContext), [i, s, a] = $r(n, [Ze.defaultSeed, e], {
    salt: `${Io}-${t || ""}`,
    override: o,
    getComputedToken: Un,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: fi,
      ignore: pi,
      preserve: gi
    }
  });
  return [n, a, t ? s : "", i, r];
}
const {
  genStyleHooks: vi
} = ai({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Qe();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, o, r] = hi();
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
    } = Qe();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), De = /* @__PURE__ */ l.createContext(null);
function gn(e) {
  const {
    getDropContainer: t,
    className: n,
    prefixCls: o,
    children: r
  } = e, {
    disabled: i
  } = l.useContext(De), [s, a] = l.useState(), [c, u] = l.useState(null);
  if (l.useEffect(() => {
    const f = t == null ? void 0 : t();
    s !== f && a(f);
  }, [t]), l.useEffect(() => {
    if (s) {
      const f = () => {
        u(!0);
      }, m = (g) => {
        g.preventDefault();
      }, y = (g) => {
        g.relatedTarget || u(!1);
      }, S = (g) => {
        u(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", f), document.addEventListener("dragover", m), document.addEventListener("dragleave", y), document.addEventListener("drop", S), () => {
        document.removeEventListener("dragenter", f), document.removeEventListener("dragover", m), document.removeEventListener("dragleave", y), document.removeEventListener("drop", S);
      };
    }
  }, [!!s]), !(t && s && !i))
    return null;
  const d = `${o}-drop-area`;
  return /* @__PURE__ */ qe(/* @__PURE__ */ l.createElement("div", {
    className: ne(d, n, {
      [`${d}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: c ? "block" : "none"
    }
  }, r), s);
}
function hn(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function bi(e) {
  return e && Z(e) === "object" && hn(e.nativeElement) ? e.nativeElement : hn(e) ? e : null;
}
function yi(e) {
  var t = bi(e);
  if (t)
    return t;
  if (e instanceof l.Component) {
    var n;
    return (n = Vt.findDOMNode) === null || n === void 0 ? void 0 : n.call(Vt, e);
  }
  return null;
}
function Si(e, t) {
  if (e == null) return {};
  var n = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    n[o] = e[o];
  }
  return n;
}
function vn(e, t) {
  if (e == null) return {};
  var n, o, r = Si(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) n = i[o], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (r[n] = e[n]);
  }
  return r;
}
var wi = /* @__PURE__ */ $.createContext({}), xi = /* @__PURE__ */ function(e) {
  tt(n, e);
  var t = nt(n);
  function n() {
    return Me(this, n), t.apply(this, arguments);
  }
  return Oe(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}($.Component);
function Ei(e) {
  var t = $.useReducer(function(a) {
    return a + 1;
  }, 0), n = J(t, 2), o = n[1], r = $.useRef(e), i = Pe(function() {
    return r.current;
  }), s = Pe(function(a) {
    r.current = typeof a == "function" ? a(r.current) : a, o();
  });
  return [i, s];
}
var be = "none", ze = "appear", He = "enter", Ue = "leave", bn = "none", le = "prepare", Re = "start", Ie = "active", Ut = "end", Bn = "prepared";
function yn(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function Ci(e, t) {
  var n = {
    animationend: yn("Animation", "AnimationEnd"),
    transitionend: yn("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var _i = Ci(rt(), typeof window < "u" ? window : {}), Vn = {};
if (rt()) {
  var Li = document.createElement("div");
  Vn = Li.style;
}
var Be = {};
function Xn(e) {
  if (Be[e])
    return Be[e];
  var t = _i[e];
  if (t)
    for (var n = Object.keys(t), o = n.length, r = 0; r < o; r += 1) {
      var i = n[r];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in Vn)
        return Be[e] = t[i], Be[e];
    }
  return "";
}
var Wn = Xn("animationend"), Gn = Xn("transitionend"), Kn = !!(Wn && Gn), Sn = Wn || "animationend", wn = Gn || "transitionend";
function xn(e, t) {
  if (!e) return null;
  if (Z(e) === "object") {
    var n = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const Ri = function(e) {
  var t = ye();
  function n(r) {
    r && (r.removeEventListener(wn, e), r.removeEventListener(Sn, e));
  }
  function o(r) {
    t.current && t.current !== r && n(t.current), r && r !== t.current && (r.addEventListener(wn, e), r.addEventListener(Sn, e), t.current = r);
  }
  return $.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [o, n];
};
var qn = rt() ? cr : xe, Zn = function(t) {
  return +setTimeout(t, 16);
}, Qn = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Zn = function(t) {
  return window.requestAnimationFrame(t);
}, Qn = function(t) {
  return window.cancelAnimationFrame(t);
});
var En = 0, Bt = /* @__PURE__ */ new Map();
function Yn(e) {
  Bt.delete(e);
}
var Ot = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  En += 1;
  var o = En;
  function r(i) {
    if (i === 0)
      Yn(o), t();
    else {
      var s = Zn(function() {
        r(i - 1);
      });
      Bt.set(o, s);
    }
  }
  return r(n), o;
};
Ot.cancel = function(e) {
  var t = Bt.get(e);
  return Yn(e), Qn(t);
};
const Ii = function() {
  var e = $.useRef(null);
  function t() {
    Ot.cancel(e.current);
  }
  function n(o) {
    var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = Ot(function() {
      r <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : n(o, r - 1);
    });
    e.current = i;
  }
  return $.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var Ti = [le, Re, Ie, Ut], Pi = [le, Bn], Jn = !1, Mi = !0;
function er(e) {
  return e === Ie || e === Ut;
}
const Oi = function(e, t, n) {
  var o = je(bn), r = J(o, 2), i = r[0], s = r[1], a = Ii(), c = J(a, 2), u = c[0], p = c[1];
  function d() {
    s(le, !0);
  }
  var f = t ? Pi : Ti;
  return qn(function() {
    if (i !== bn && i !== Ut) {
      var m = f.indexOf(i), y = f[m + 1], S = n(i);
      S === Jn ? s(y, !0) : y && u(function(g) {
        function v() {
          g.isCanceled() || s(y, !0);
        }
        S === !0 ? v() : Promise.resolve(S).then(v);
      });
    }
  }, [e, i]), $.useEffect(function() {
    return function() {
      p();
    };
  }, []), [d, i];
};
function Fi(e, t, n, o) {
  var r = o.motionEnter, i = r === void 0 ? !0 : r, s = o.motionAppear, a = s === void 0 ? !0 : s, c = o.motionLeave, u = c === void 0 ? !0 : c, p = o.motionDeadline, d = o.motionLeaveImmediately, f = o.onAppearPrepare, m = o.onEnterPrepare, y = o.onLeavePrepare, S = o.onAppearStart, g = o.onEnterStart, v = o.onLeaveStart, x = o.onAppearActive, E = o.onEnterActive, b = o.onLeaveActive, w = o.onAppearEnd, h = o.onEnterEnd, L = o.onLeaveEnd, R = o.onVisibleChanged, F = je(), C = J(F, 2), M = C[0], _ = C[1], O = Ei(be), P = J(O, 2), A = P[0], D = P[1], U = je(null), W = J(U, 2), ge = W[0], ce = W[1], V = A(), N = ye(!1), G = ye(null);
  function H() {
    return n();
  }
  var Q = ye(!1);
  function pe() {
    D(be), ce(null, !0);
  }
  var ae = Pe(function(q) {
    var B = A();
    if (B !== be) {
      var te = H();
      if (!(q && !q.deadline && q.target !== te)) {
        var z = Q.current, _e;
        B === ze && z ? _e = w == null ? void 0 : w(te, q) : B === He && z ? _e = h == null ? void 0 : h(te, q) : B === Ue && z && (_e = L == null ? void 0 : L(te, q)), z && _e !== !1 && pe();
      }
    }
  }), Fe = Ri(ae), me = J(Fe, 1), ue = me[0], he = function(B) {
    switch (B) {
      case ze:
        return T(T(T({}, le, f), Re, S), Ie, x);
      case He:
        return T(T(T({}, le, m), Re, g), Ie, E);
      case Ue:
        return T(T(T({}, le, y), Re, v), Ie, b);
      default:
        return {};
    }
  }, de = $.useMemo(function() {
    return he(V);
  }, [V]), Se = Oi(V, !e, function(q) {
    if (q === le) {
      var B = de[le];
      return B ? B(H()) : Jn;
    }
    if (j in de) {
      var te;
      ce(((te = de[j]) === null || te === void 0 ? void 0 : te.call(de, H(), null)) || null);
    }
    return j === Ie && V !== be && (ue(H()), p > 0 && (clearTimeout(G.current), G.current = setTimeout(function() {
      ae({
        deadline: !0
      });
    }, p))), j === Bn && pe(), Mi;
  }), Ce = J(Se, 2), re = Ce[0], j = Ce[1], oe = er(j);
  Q.current = oe;
  var ve = ye(null);
  qn(function() {
    if (!(N.current && ve.current === t)) {
      _(t);
      var q = N.current;
      N.current = !0;
      var B;
      !q && t && a && (B = ze), q && t && i && (B = He), (q && !t && u || !q && d && !t && u) && (B = Ue);
      var te = he(B);
      B && (e || te[le]) ? (D(B), re()) : D(be), ve.current = t;
    }
  }, [t]), xe(function() {
    // Cancel appear
    (V === ze && !a || // Cancel enter
    V === He && !i || // Cancel leave
    V === Ue && !u) && D(be);
  }, [a, i, u]), xe(function() {
    return function() {
      N.current = !1, clearTimeout(G.current);
    };
  }, []);
  var K = $.useRef(!1);
  xe(function() {
    M && (K.current = !0), M !== void 0 && V === be && ((K.current || M) && (R == null || R(M)), K.current = !0);
  }, [M, V]);
  var we = ge;
  return de[le] && j === Re && (we = I({
    transition: "none"
  }, we)), [V, j, we, M ?? t];
}
function Ai(e) {
  var t = e;
  Z(e) === "object" && (t = e.transitionSupport);
  function n(r, i) {
    return !!(r.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ $.forwardRef(function(r, i) {
    var s = r.visible, a = s === void 0 ? !0 : s, c = r.removeOnLeave, u = c === void 0 ? !0 : c, p = r.forceRender, d = r.children, f = r.motionName, m = r.leavedClassName, y = r.eventProps, S = $.useContext(wi), g = S.motion, v = n(r, g), x = ye(), E = ye();
    function b() {
      try {
        return x.current instanceof HTMLElement ? x.current : yi(E.current);
      } catch {
        return null;
      }
    }
    var w = Fi(v, a, b, r), h = J(w, 4), L = h[0], R = h[1], F = h[2], C = h[3], M = $.useRef(C);
    C && (M.current = !0);
    var _ = $.useCallback(function(W) {
      x.current = W, Qo(i, W);
    }, [i]), O, P = I(I({}, y), {}, {
      visible: a
    });
    if (!d)
      O = null;
    else if (L === be)
      C ? O = d(I({}, P), _) : !u && M.current && m ? O = d(I(I({}, P), {}, {
        className: m
      }), _) : p || !u && !m ? O = d(I(I({}, P), {}, {
        style: {
          display: "none"
        }
      }), _) : O = null;
    else {
      var A;
      R === le ? A = "prepare" : er(R) ? A = "active" : R === Re && (A = "start");
      var D = xn(f, "".concat(L, "-").concat(A));
      O = d(I(I({}, P), {}, {
        className: ne(xn(f, L), T(T({}, D, D && A), f, typeof f == "string")),
        style: F
      }), _);
    }
    if (/* @__PURE__ */ $.isValidElement(O) && Yo(O)) {
      var U = Jo(O);
      U || (O = /* @__PURE__ */ $.cloneElement(O, {
        ref: _
      }));
    }
    return /* @__PURE__ */ $.createElement(xi, {
      ref: E
    }, O);
  });
  return o.displayName = "CSSMotion", o;
}
const $i = Ai(Kn);
var Ft = "add", At = "keep", $t = "remove", Ct = "removed";
function ki(e) {
  var t;
  return e && Z(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, I(I({}, t), {}, {
    key: String(t.key)
  });
}
function kt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(ki);
}
function ji() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], o = 0, r = t.length, i = kt(e), s = kt(t);
  i.forEach(function(u) {
    for (var p = !1, d = o; d < r; d += 1) {
      var f = s[d];
      if (f.key === u.key) {
        o < d && (n = n.concat(s.slice(o, d).map(function(m) {
          return I(I({}, m), {}, {
            status: Ft
          });
        })), o = d), n.push(I(I({}, f), {}, {
          status: At
        })), o += 1, p = !0;
        break;
      }
    }
    p || n.push(I(I({}, u), {}, {
      status: $t
    }));
  }), o < r && (n = n.concat(s.slice(o).map(function(u) {
    return I(I({}, u), {}, {
      status: Ft
    });
  })));
  var a = {};
  n.forEach(function(u) {
    var p = u.key;
    a[p] = (a[p] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(u) {
    return a[u] > 1;
  });
  return c.forEach(function(u) {
    n = n.filter(function(p) {
      var d = p.key, f = p.status;
      return d !== u || f !== $t;
    }), n.forEach(function(p) {
      p.key === u && (p.status = At);
    });
  }), n;
}
var Di = ["component", "children", "onVisibleChanged", "onAllRemoved"], Ni = ["status"], zi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function Hi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : $i, n = /* @__PURE__ */ function(o) {
    tt(i, o);
    var r = nt(i);
    function i() {
      var s;
      Me(this, i);
      for (var a = arguments.length, c = new Array(a), u = 0; u < a; u++)
        c[u] = arguments[u];
      return s = r.call.apply(r, [this].concat(c)), T(Ee(s), "state", {
        keyEntities: []
      }), T(Ee(s), "removeKey", function(p) {
        s.setState(function(d) {
          var f = d.keyEntities.map(function(m) {
            return m.key !== p ? m : I(I({}, m), {}, {
              status: Ct
            });
          });
          return {
            keyEntities: f
          };
        }, function() {
          var d = s.state.keyEntities, f = d.filter(function(m) {
            var y = m.status;
            return y !== Ct;
          }).length;
          f === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Oe(i, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, u = this.props, p = u.component, d = u.children, f = u.onVisibleChanged;
        u.onAllRemoved;
        var m = vn(u, Di), y = p || $.Fragment, S = {};
        return zi.forEach(function(g) {
          S[g] = m[g], delete m[g];
        }), delete m.keys, /* @__PURE__ */ $.createElement(y, m, c.map(function(g, v) {
          var x = g.status, E = vn(g, Ni), b = x === Ft || x === At;
          return /* @__PURE__ */ $.createElement(t, Te({}, S, {
            key: E.key,
            visible: b,
            eventProps: E,
            onVisibleChanged: function(h) {
              f == null || f(h, {
                key: E.key
              }), h || a.removeKey(E.key);
            }
          }), function(w, h) {
            return d(I(I({}, w), {}, {
              index: v
            }), h);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var u = a.keys, p = c.keyEntities, d = kt(u), f = ji(p, d);
        return {
          keyEntities: f.filter(function(m) {
            var y = p.find(function(S) {
              var g = S.key;
              return m.key === g;
            });
            return !(y && y.status === Ct && m.status === $t);
          })
        };
      }
    }]), i;
  }($.Component);
  return T(n, "defaultProps", {
    component: "div"
  }), n;
}
const Ui = Hi(Kn);
function Bi(e, t) {
  const {
    children: n,
    upload: o,
    rootClassName: r
  } = e, i = l.useRef(null);
  return l.useImperativeHandle(t, () => i.current), /* @__PURE__ */ l.createElement(Rn, Te({}, o, {
    showUploadList: !1,
    rootClassName: r,
    ref: i
  }), n);
}
const tr = /* @__PURE__ */ l.forwardRef(Bi), Vi = (e) => {
  const {
    componentCls: t,
    antCls: n,
    calc: o
  } = e, r = `${t}-list-card`, i = o(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [r]: {
      borderRadius: e.borderRadius,
      position: "relative",
      background: e.colorFillContent,
      borderWidth: e.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${r}-name,${r}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${r}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${r}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: o(e.paddingSM).sub(e.lineWidth).equal(),
        paddingInlineStart: o(e.padding).add(e.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: e.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${r}-icon`]: {
          fontSize: o(e.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: o(e.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${r}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${r}-desc`]: {
          color: e.colorTextTertiary
        }
      },
      // ============================== Preview ==============================
      "&-type-preview": {
        width: i,
        height: i,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${r}-status-error)`]: {
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
        [`${r}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${e.opacityLoading})`
        },
        // Error
        [`&${r}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${r}-img-mask`]: {
            borderRadius: o(e.borderRadius).sub(e.lineWidth).equal()
          },
          [`${r}-desc`]: {
            paddingInline: e.paddingXXS
          }
        },
        // Progress
        [`${r}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${r}-remove`]: {
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
      [`&:hover ${r}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: e.colorError,
        [`${r}-desc`]: {
          color: e.colorError
        }
      },
      // ============================== Motion ===============================
      "&-motion": {
        transition: ["opacity", "width", "margin", "padding"].map((s) => `${s} ${e.motionDurationSlow}`).join(","),
        "&-appear-start": {
          width: 0,
          transition: "none"
        },
        "&-leave-active": {
          opacity: 0,
          width: 0,
          paddingInline: 0,
          borderInlineWidth: 0,
          marginInlineEnd: o(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, jt = {
  "&, *": {
    boxSizing: "border-box"
  }
}, Xi = (e) => {
  const {
    componentCls: t,
    calc: n,
    antCls: o
  } = e, r = `${t}-drop-area`, i = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [r]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...jt,
      "&-on-body": {
        position: "fixed",
        inset: 0
      },
      "&-hide-placement": {
        [`${i}-inner`]: {
          display: "none"
        }
      },
      [i]: {
        padding: 0
      }
    },
    "&": {
      // ============================= Placeholder =============================
      [i]: {
        height: "100%",
        borderRadius: e.borderRadius,
        borderWidth: e.lineWidthBold,
        borderStyle: "dashed",
        borderColor: "transparent",
        padding: e.padding,
        position: "relative",
        backdropFilter: "blur(10px)",
        background: e.colorBgPlaceholderHover,
        ...jt,
        [`${o}-upload-wrapper ${o}-upload${o}-upload-btn`]: {
          padding: 0
        },
        [`&${i}-drag-in`]: {
          borderColor: e.colorPrimaryHover
        },
        [`&${i}-disabled`]: {
          opacity: 0.25,
          pointerEvents: "none"
        },
        [`${i}-inner`]: {
          gap: n(e.paddingXXS).div(2).equal()
        },
        [`${i}-icon`]: {
          fontSize: e.fontSizeHeading2,
          lineHeight: 1
        },
        [`${i}-title${i}-title`]: {
          margin: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight
        },
        [`${i}-description`]: {}
      }
    }
  };
}, Wi = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, o = `${t}-list`, r = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...jt,
      // =============================== File List ===============================
      [o]: {
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
          maxHeight: n(r).mul(3).equal(),
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
          width: r,
          height: r,
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
          [`&${o}-overflow-ping-start ${o}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${o}-overflow-ping-end ${o}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${o}-overflow-ping-end ${o}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${o}-overflow-ping-start ${o}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, Gi = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new fe(t).setA(0.85).toRgbString()
  };
}, nr = vi("Attachments", (e) => {
  const t = Ht(e, {});
  return [Xi(t), Wi(t), Vi(t)];
}, Gi), Ki = (e) => e.indexOf("image/") === 0, Ve = 200;
function qi(e) {
  return new Promise((t) => {
    if (!e || !e.type || !Ki(e.type)) {
      t("");
      return;
    }
    const n = new Image();
    if (n.onload = () => {
      const {
        width: o,
        height: r
      } = n, i = o / r, s = i > 1 ? Ve : Ve * i, a = i > 1 ? Ve / i : Ve, c = document.createElement("canvas");
      c.width = s, c.height = a, c.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(c), c.getContext("2d").drawImage(n, 0, 0, s, a);
      const p = c.toDataURL();
      document.body.removeChild(c), window.URL.revokeObjectURL(n.src), t(p);
    }, n.crossOrigin = "anonymous", e.type.startsWith("image/svg+xml")) {
      const o = new FileReader();
      o.onload = () => {
        o.result && typeof o.result == "string" && (n.src = o.result);
      }, o.readAsDataURL(e);
    } else if (e.type.startsWith("image/gif")) {
      const o = new FileReader();
      o.onload = () => {
        o.result && t(o.result);
      }, o.readAsDataURL(e);
    } else
      n.src = window.URL.createObjectURL(e);
  });
}
function Zi() {
  return /* @__PURE__ */ l.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ l.createElement("title", null, "audio"), /* @__PURE__ */ l.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ l.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function Qi(e) {
  const {
    percent: t
  } = e, {
    token: n
  } = Ze.useToken();
  return /* @__PURE__ */ l.createElement(br, {
    type: "circle",
    percent: t,
    size: n.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (o) => /* @__PURE__ */ l.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (o || 0).toFixed(0), "%")
  });
}
function Yi() {
  return /* @__PURE__ */ l.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ l.createElement("title", null, "video"), /* @__PURE__ */ l.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ l.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const _t = " ", Dt = "#8c8c8c", rr = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], Ji = [{
  icon: /* @__PURE__ */ l.createElement(Er, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  icon: /* @__PURE__ */ l.createElement(Cr, null),
  color: Dt,
  ext: rr
}, {
  icon: /* @__PURE__ */ l.createElement(_r, null),
  color: Dt,
  ext: ["md", "mdx"]
}, {
  icon: /* @__PURE__ */ l.createElement(Lr, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  icon: /* @__PURE__ */ l.createElement(Rr, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  icon: /* @__PURE__ */ l.createElement(Ir, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  icon: /* @__PURE__ */ l.createElement(Tr, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  icon: /* @__PURE__ */ l.createElement(Yi, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  icon: /* @__PURE__ */ l.createElement(Zi, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function Cn(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
function es(e) {
  let t = e;
  const n = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let o = 0;
  for (; t >= 1024 && o < n.length - 1; )
    t /= 1024, o++;
  return `${t.toFixed(0)} ${n[o]}`;
}
function ts(e, t) {
  const {
    prefixCls: n,
    item: o,
    onRemove: r,
    className: i,
    style: s,
    imageProps: a
  } = e, c = l.useContext(De), {
    disabled: u
  } = c || {}, {
    name: p,
    size: d,
    percent: f,
    status: m = "done",
    description: y
  } = o, {
    getPrefixCls: S
  } = Qe(), g = S("attachment", n), v = `${g}-list-card`, [x, E, b] = nr(g), [w, h] = l.useMemo(() => {
    const D = p || "", U = D.match(/^(.*)\.[^.]+$/);
    return U ? [U[1], D.slice(U[1].length)] : [D, ""];
  }, [p]), L = l.useMemo(() => Cn(h, rr), [h]), R = l.useMemo(() => y || (m === "uploading" ? `${f || 0}%` : m === "error" ? o.response || _t : d ? es(d) : _t), [m, f]), [F, C] = l.useMemo(() => {
    for (const {
      ext: D,
      icon: U,
      color: W
    } of Ji)
      if (Cn(h, D))
        return [U, W];
    return [/* @__PURE__ */ l.createElement(wr, {
      key: "defaultIcon"
    }), Dt];
  }, [h]), [M, _] = l.useState();
  l.useEffect(() => {
    if (o.originFileObj) {
      let D = !0;
      return qi(o.originFileObj).then((U) => {
        D && _(U);
      }), () => {
        D = !1;
      };
    }
    _(void 0);
  }, [o.originFileObj]);
  let O = null;
  const P = o.thumbUrl || o.url || M, A = L && (o.originFileObj || P);
  return A ? O = /* @__PURE__ */ l.createElement(l.Fragment, null, P && /* @__PURE__ */ l.createElement(yr, Te({
    alt: "preview",
    src: P
  }, a)), m !== "done" && /* @__PURE__ */ l.createElement("div", {
    className: `${v}-img-mask`
  }, m === "uploading" && f !== void 0 && /* @__PURE__ */ l.createElement(Qi, {
    percent: f,
    prefixCls: v
  }), m === "error" && /* @__PURE__ */ l.createElement("div", {
    className: `${v}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${v}-ellipsis-prefix`
  }, R)))) : O = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement("div", {
    className: `${v}-icon`,
    style: {
      color: C
    }
  }, F), /* @__PURE__ */ l.createElement("div", {
    className: `${v}-content`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${v}-name`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${v}-ellipsis-prefix`
  }, w ?? _t), /* @__PURE__ */ l.createElement("div", {
    className: `${v}-ellipsis-suffix`
  }, h)), /* @__PURE__ */ l.createElement("div", {
    className: `${v}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${v}-ellipsis-prefix`
  }, R)))), x(/* @__PURE__ */ l.createElement("div", {
    className: ne(v, {
      [`${v}-status-${m}`]: m,
      [`${v}-type-preview`]: A,
      [`${v}-type-overview`]: !A
    }, i, E, b),
    style: s,
    ref: t
  }, O, !u && r && /* @__PURE__ */ l.createElement("button", {
    type: "button",
    className: `${v}-remove`,
    onClick: () => {
      r(o);
    }
  }, /* @__PURE__ */ l.createElement(xr, null))));
}
const or = /* @__PURE__ */ l.forwardRef(ts), _n = 1;
function ns(e) {
  const {
    prefixCls: t,
    items: n,
    onRemove: o,
    overflow: r,
    upload: i,
    listClassName: s,
    listStyle: a,
    itemClassName: c,
    uploadClassName: u,
    uploadStyle: p,
    itemStyle: d,
    imageProps: f
  } = e, m = `${t}-list`, y = l.useRef(null), [S, g] = l.useState(!1), {
    disabled: v
  } = l.useContext(De);
  l.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [x, E] = l.useState(!1), [b, w] = l.useState(!1), h = () => {
    const C = y.current;
    C && (r === "scrollX" ? (E(Math.abs(C.scrollLeft) >= _n), w(C.scrollWidth - C.clientWidth - Math.abs(C.scrollLeft) >= _n)) : r === "scrollY" && (E(C.scrollTop !== 0), w(C.scrollHeight - C.clientHeight !== C.scrollTop)));
  };
  l.useEffect(() => {
    h();
  }, [r, n.length]);
  const L = (C) => {
    const M = y.current;
    M && M.scrollTo({
      left: M.scrollLeft + C * M.clientWidth,
      behavior: "smooth"
    });
  }, R = () => {
    L(-1);
  }, F = () => {
    L(1);
  };
  return /* @__PURE__ */ l.createElement("div", {
    className: ne(m, {
      [`${m}-overflow-${e.overflow}`]: r,
      [`${m}-overflow-ping-start`]: x,
      [`${m}-overflow-ping-end`]: b
    }, s),
    ref: y,
    onScroll: h,
    style: a
  }, /* @__PURE__ */ l.createElement(Ui, {
    keys: n.map((C) => ({
      key: C.uid,
      item: C
    })),
    motionName: `${m}-card-motion`,
    component: !1,
    motionAppear: S,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: C,
    item: M,
    className: _,
    style: O
  }) => /* @__PURE__ */ l.createElement(or, {
    key: C,
    prefixCls: t,
    item: M,
    onRemove: o,
    className: ne(_, c),
    imageProps: f,
    style: {
      ...O,
      ...d
    }
  })), !v && /* @__PURE__ */ l.createElement(tr, {
    upload: i
  }, /* @__PURE__ */ l.createElement(mt, {
    className: ne(u, `${m}-upload-btn`),
    style: p,
    type: "dashed"
  }, /* @__PURE__ */ l.createElement(Pr, {
    className: `${m}-upload-btn-icon`
  }))), r === "scrollX" && /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(mt, {
    size: "small",
    shape: "circle",
    className: `${m}-prev-btn`,
    icon: /* @__PURE__ */ l.createElement(Mr, null),
    onClick: R
  }), /* @__PURE__ */ l.createElement(mt, {
    size: "small",
    shape: "circle",
    className: `${m}-next-btn`,
    icon: /* @__PURE__ */ l.createElement(Or, null),
    onClick: F
  })));
}
function rs(e, t) {
  const {
    prefixCls: n,
    placeholder: o = {},
    upload: r,
    className: i,
    style: s
  } = e, a = `${n}-placeholder`, c = o || {}, {
    disabled: u
  } = l.useContext(De), [p, d] = l.useState(!1), f = () => {
    d(!0);
  }, m = (g) => {
    g.currentTarget.contains(g.relatedTarget) || d(!1);
  }, y = () => {
    d(!1);
  }, S = /* @__PURE__ */ l.isValidElement(o) ? o : /* @__PURE__ */ l.createElement(Sr, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ l.createElement(gt.Text, {
    className: `${a}-icon`
  }, c.icon), /* @__PURE__ */ l.createElement(gt.Title, {
    className: `${a}-title`,
    level: 5
  }, c.title), /* @__PURE__ */ l.createElement(gt.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, c.description));
  return /* @__PURE__ */ l.createElement("div", {
    className: ne(a, {
      [`${a}-drag-in`]: p,
      [`${a}-disabled`]: u
    }, i),
    onDragEnter: f,
    onDragLeave: m,
    onDrop: y,
    "aria-hidden": u,
    style: s
  }, /* @__PURE__ */ l.createElement(Rn.Dragger, Te({
    showUploadList: !1
  }, r, {
    ref: t,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), S));
}
const os = /* @__PURE__ */ l.forwardRef(rs);
function is(e, t) {
  const {
    prefixCls: n,
    rootClassName: o,
    rootStyle: r,
    className: i,
    style: s,
    items: a,
    children: c,
    getDropContainer: u,
    placeholder: p,
    onChange: d,
    onRemove: f,
    overflow: m,
    imageProps: y,
    disabled: S,
    classNames: g = {},
    styles: v = {},
    ...x
  } = e, {
    getPrefixCls: E,
    direction: b
  } = Qe(), w = E("attachment", n), h = Oo("attachments"), {
    classNames: L,
    styles: R
  } = h, F = l.useRef(null), C = l.useRef(null);
  l.useImperativeHandle(t, () => ({
    nativeElement: F.current,
    upload: (N) => {
      var H, Q;
      const G = (Q = (H = C.current) == null ? void 0 : H.nativeElement) == null ? void 0 : Q.querySelector('input[type="file"]');
      if (G) {
        const pe = new DataTransfer();
        pe.items.add(N), G.files = pe.files, G.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [M, _, O] = nr(w), P = ne(_, O), [A, D] = Bo([], {
    value: a
  }), U = Pe((N) => {
    D(N.fileList), d == null || d(N);
  }), W = {
    ...x,
    fileList: A,
    onChange: U
  }, ge = (N) => Promise.resolve(typeof f == "function" ? f(N) : f).then((G) => {
    if (G === !1)
      return;
    const H = A.filter((Q) => Q.uid !== N.uid);
    U({
      file: {
        ...N,
        status: "removed"
      },
      fileList: H
    });
  });
  let ce;
  const V = (N, G, H) => {
    const Q = typeof p == "function" ? p(N) : p;
    return /* @__PURE__ */ l.createElement(os, {
      placeholder: Q,
      upload: W,
      prefixCls: w,
      className: ne(L.placeholder, g.placeholder),
      style: {
        ...R.placeholder,
        ...v.placeholder,
        ...G == null ? void 0 : G.style
      },
      ref: H
    });
  };
  if (c)
    ce = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(tr, {
      upload: W,
      rootClassName: o,
      ref: C
    }, c), /* @__PURE__ */ l.createElement(gn, {
      getDropContainer: u,
      prefixCls: w,
      className: ne(P, o)
    }, V("drop")));
  else {
    const N = A.length > 0;
    ce = /* @__PURE__ */ l.createElement("div", {
      className: ne(w, P, {
        [`${w}-rtl`]: b === "rtl"
      }, i, o),
      style: {
        ...r,
        ...s
      },
      dir: b || "ltr",
      ref: F
    }, /* @__PURE__ */ l.createElement(ns, {
      prefixCls: w,
      items: A,
      onRemove: ge,
      overflow: m,
      upload: W,
      listClassName: ne(L.list, g.list),
      listStyle: {
        ...R.list,
        ...v.list,
        ...!N && {
          display: "none"
        }
      },
      uploadClassName: ne(L.upload, g.upload),
      uploadStyle: {
        ...R.upload,
        ...v.upload
      },
      itemClassName: ne(L.item, g.item),
      itemStyle: {
        ...R.item,
        ...v.item
      },
      imageProps: y
    }), V("inline", N ? {
      style: {
        display: "none"
      }
    } : {}, C), /* @__PURE__ */ l.createElement(gn, {
      getDropContainer: u || (() => F.current),
      prefixCls: w,
      className: P
    }, V("drop")));
  }
  return M(/* @__PURE__ */ l.createElement(De.Provider, {
    value: {
      disabled: S
    }
  }, ce));
}
const ir = /* @__PURE__ */ l.forwardRef(is);
ir.FileCard = or;
function ss(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function as(e, t = !1) {
  try {
    if (mr(e))
      return e;
    if (t && !ss(e))
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
function Y(e, t) {
  return Je(() => as(e, t), [e, t]);
}
function ls(e, t) {
  const n = Je(() => l.Children.toArray(e.originalChildren || e).filter((i) => i.props.node && !i.props.node.ignore && (!i.props.nodeSlotKey || t)).sort((i, s) => {
    if (i.props.node.slotIndex && s.props.node.slotIndex) {
      const a = $e(i.props.node.slotIndex) || 0, c = $e(s.props.node.slotIndex) || 0;
      return a - c === 0 && i.props.node.subSlotIndex && s.props.node.subSlotIndex ? ($e(i.props.node.subSlotIndex) || 0) - ($e(s.props.node.subSlotIndex) || 0) : a - c;
    }
    return 0;
  }).map((i) => i.props.node.target), [e, t]);
  return Eo(n);
}
function cs(e, t) {
  return Object.keys(e).reduce((n, o) => (e[o] !== void 0 && (n[o] = e[o]), n), {});
}
const us = ({
  children: e,
  ...t
}) => /* @__PURE__ */ ee.jsx(ee.Fragment, {
  children: e(t)
});
function ds(e) {
  return l.createElement(us, {
    children: e
  });
}
function Ln(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ds((n) => /* @__PURE__ */ ee.jsx(hr, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ ee.jsx(ke, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ ee.jsx(ke, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ie({
  key: e,
  slots: t,
  targets: n
}, o) {
  return t[e] ? (...r) => n ? n.map((i, s) => /* @__PURE__ */ ee.jsx(l.Fragment, {
    children: Ln(i, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ ee.jsx(ee.Fragment, {
    children: Ln(t[e], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const fs = (e) => !!e.name;
function Lt(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const gs = wo(({
  slots: e,
  upload: t,
  showUploadList: n,
  progress: o,
  beforeUpload: r,
  customRequest: i,
  previewFile: s,
  isImageUrl: a,
  itemRender: c,
  iconRender: u,
  data: p,
  onChange: d,
  onValueChange: f,
  onRemove: m,
  items: y,
  setSlotParams: S,
  placeholder: g,
  getDropContainer: v,
  children: x,
  maxCount: E,
  imageProps: b,
  ...w
}) => {
  const h = Lt(b == null ? void 0 : b.preview), L = e["imageProps.preview.mask"] || e["imageProps.preview.closeIcon"] || e["imageProps.preview.toolbarRender"] || e["imageProps.preview.imageRender"] || (b == null ? void 0 : b.preview) !== !1, R = Y(h.getContainer), F = Y(h.toolbarRender), C = Y(h.imageRender), M = e["showUploadList.downloadIcon"] || e["showUploadList.removeIcon"] || e["showUploadList.previewIcon"] || e["showUploadList.extra"] || typeof n == "object", _ = Lt(n), O = e["placeholder.title"] || e["placeholder.description"] || e["placeholder.icon"] || typeof g == "object", P = Lt(g), A = Y(_.showPreviewIcon), D = Y(_.showRemoveIcon), U = Y(_.showDownloadIcon), W = Y(r), ge = Y(i), ce = Y(o == null ? void 0 : o.format), V = Y(s), N = Y(a), G = Y(c), H = Y(u), Q = Y(g, !0), pe = Y(v), ae = Y(p), [Fe, me] = Ke(!1), [ue, he] = Ke(y);
  xe(() => {
    he(y);
  }, [y]);
  const de = Je(() => {
    const re = {};
    return ue.map((j) => {
      if (!fs(j)) {
        const oe = j.uid || j.url || j.path;
        return re[oe] || (re[oe] = 0), re[oe]++, {
          ...j,
          name: j.orig_name || j.path,
          uid: j.uid || oe + "-" + re[oe],
          status: "done"
        };
      }
      return j;
    }) || [];
  }, [ue]), Se = ls(x), Ce = w.disabled || Fe;
  return /* @__PURE__ */ ee.jsxs(ee.Fragment, {
    children: [/* @__PURE__ */ ee.jsx("div", {
      style: {
        display: "none"
      },
      children: Se.length > 0 ? null : x
    }), /* @__PURE__ */ ee.jsx(ir, {
      ...w,
      disabled: Ce,
      imageProps: {
        ...b,
        preview: L ? cs({
          ...h,
          getContainer: R,
          toolbarRender: e["imageProps.preview.toolbarRender"] ? ie({
            slots: e,
            key: "imageProps.preview.toolbarRender"
          }) : F,
          imageRender: e["imageProps.preview.imageRender"] ? ie({
            slots: e,
            key: "imageProps.preview.imageRender"
          }) : C,
          ...e["imageProps.preview.mask"] || Reflect.has(h, "mask") ? {
            mask: e["imageProps.preview.mask"] ? /* @__PURE__ */ ee.jsx(ke, {
              slot: e["imageProps.preview.mask"]
            }) : h.mask
          } : {},
          closeIcon: e["imageProps.preview.closeIcon"] ? /* @__PURE__ */ ee.jsx(ke, {
            slot: e["imageProps.preview.closeIcon"]
          }) : h.closeIcon
        }) : !1,
        placeholder: e["imageProps.placeholder"] ? /* @__PURE__ */ ee.jsx(ke, {
          slot: e["imageProps.placeholder"]
        }) : b == null ? void 0 : b.placeholder
      },
      getDropContainer: pe,
      placeholder: e.placeholder ? ie({
        slots: e,
        key: "placeholder"
      }) : O ? (...re) => {
        var j, oe, ve;
        return {
          ...P,
          icon: e["placeholder.icon"] ? (j = ie({
            slots: e,
            key: "placeholder.icon"
          })) == null ? void 0 : j(...re) : P.icon,
          title: e["placeholder.title"] ? (oe = ie({
            slots: e,
            key: "placeholder.title"
          })) == null ? void 0 : oe(...re) : P.title,
          description: e["placeholder.description"] ? (ve = ie({
            slots: e,
            key: "placeholder.description"
          })) == null ? void 0 : ve(...re) : P.description
        };
      } : Q || g,
      items: de,
      data: ae || p,
      previewFile: V,
      isImageUrl: N,
      itemRender: e.itemRender ? ie({
        slots: e,
        key: "itemRender"
      }) : G,
      iconRender: e.iconRender ? ie({
        slots: e,
        key: "iconRender"
      }) : H,
      maxCount: E,
      onChange: async (re) => {
        try {
          const j = re.file, oe = re.fileList, ve = de.findIndex((K) => K.uid === j.uid);
          if (ve !== -1) {
            if (Ce)
              return;
            m == null || m(j);
            const K = ue.slice();
            K.splice(ve, 1), f == null || f(K), d == null || d(K.map((we) => we.path));
          } else {
            if (W && !await W(j, oe) || Ce)
              return;
            me(!0);
            let K = oe.filter((z) => z.status !== "done");
            if (E === 1)
              K = K.slice(0, 1);
            else if (K.length === 0) {
              me(!1);
              return;
            } else if (typeof E == "number") {
              const z = E - ue.length;
              K = K.slice(0, z < 0 ? 0 : z);
            }
            const we = ue, q = K.map((z) => ({
              ...z,
              size: z.size,
              uid: z.uid,
              name: z.name,
              status: "uploading"
            }));
            he((z) => [...E === 1 ? [] : z, ...q]);
            const B = (await t(K.map((z) => z.originFileObj))).filter(Boolean).map((z, _e) => ({
              ...z,
              uid: q[_e].uid
            })), te = E === 1 ? B : [...we, ...B];
            me(!1), he(te), f == null || f(te), d == null || d(te.map((z) => z.path));
          }
        } catch (j) {
          console.error(j), me(!1);
        }
      },
      customRequest: ge || Vr,
      progress: o && {
        ...o,
        format: ce
      },
      showUploadList: M ? {
        ..._,
        showDownloadIcon: U || _.showDownloadIcon,
        showRemoveIcon: D || _.showRemoveIcon,
        showPreviewIcon: A || _.showPreviewIcon,
        downloadIcon: e["showUploadList.downloadIcon"] ? ie({
          slots: e,
          key: "showUploadList.downloadIcon"
        }) : _.downloadIcon,
        removeIcon: e["showUploadList.removeIcon"] ? ie({
          slots: e,
          key: "showUploadList.removeIcon"
        }) : _.removeIcon,
        previewIcon: e["showUploadList.previewIcon"] ? ie({
          slots: e,
          key: "showUploadList.previewIcon"
        }) : _.previewIcon,
        extra: e["showUploadList.extra"] ? ie({
          slots: e,
          key: "showUploadList.extra"
        }) : _.extra
      } : n,
      children: Se.length > 0 ? x : void 0
    })]
  });
});
export {
  gs as Attachments,
  gs as default
};
