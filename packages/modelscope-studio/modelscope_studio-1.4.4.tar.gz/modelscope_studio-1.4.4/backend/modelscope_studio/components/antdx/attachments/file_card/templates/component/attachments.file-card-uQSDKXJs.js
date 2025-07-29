var Nt = (e) => {
  throw TypeError(e);
};
var zt = (e, t, r) => t.has(e) || Nt("Cannot " + r);
var de = (e, t, r) => (zt(e, t, "read from private field"), r ? r.call(e) : t.get(e)), Ht = (e, t, r) => t.has(e) ? Nt("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, r), Bt = (e, t, r, n) => (zt(e, t, "write to private field"), n ? n.call(e, r) : t.set(e, r), r);
import { i as gn, a as St, r as hn, Z as je, g as vn, b as bn, c as Q } from "./Index-CrrqCUys.js";
const $ = window.ms_globals.React, l = window.ms_globals.React, un = window.ms_globals.React.forwardRef, se = window.ms_globals.React.useRef, fn = window.ms_globals.React.useState, xe = window.ms_globals.React.useEffect, Tr = window.ms_globals.React.useMemo, dn = window.ms_globals.React.version, pn = window.ms_globals.React.isValidElement, mn = window.ms_globals.React.useLayoutEffect, Vt = window.ms_globals.ReactDOM, ze = window.ms_globals.ReactDOM.createPortal, yn = window.ms_globals.internalContext.useContextPropsContext, Sn = window.ms_globals.internalContext.ContextPropsProvider, xn = window.ms_globals.antd.ConfigProvider, He = window.ms_globals.antd.theme, Lr = window.ms_globals.antd.Upload, wn = window.ms_globals.antd.Progress, En = window.ms_globals.antd.Image, at = window.ms_globals.antd.Button, Cn = window.ms_globals.antd.Flex, lt = window.ms_globals.antd.Typography, _n = window.ms_globals.antdIcons.FileTextFilled, Rn = window.ms_globals.antdIcons.CloseCircleFilled, Tn = window.ms_globals.antdIcons.FileExcelFilled, Ln = window.ms_globals.antdIcons.FileImageFilled, Pn = window.ms_globals.antdIcons.FileMarkdownFilled, Mn = window.ms_globals.antdIcons.FilePdfFilled, In = window.ms_globals.antdIcons.FilePptFilled, On = window.ms_globals.antdIcons.FileWordFilled, $n = window.ms_globals.antdIcons.FileZipFilled, An = window.ms_globals.antdIcons.PlusOutlined, Fn = window.ms_globals.antdIcons.LeftOutlined, kn = window.ms_globals.antdIcons.RightOutlined, Ut = window.ms_globals.antdCssinjs.unit, ct = window.ms_globals.antdCssinjs.token2CSSVar, Xt = window.ms_globals.antdCssinjs.useStyleRegister, jn = window.ms_globals.antdCssinjs.useCSSVarRegister, Dn = window.ms_globals.antdCssinjs.createTheme, Nn = window.ms_globals.antdCssinjs.useCacheToken;
var zn = /\s/;
function Hn(e) {
  for (var t = e.length; t-- && zn.test(e.charAt(t)); )
    ;
  return t;
}
var Bn = /^\s+/;
function Vn(e) {
  return e && e.slice(0, Hn(e) + 1).replace(Bn, "");
}
var Wt = NaN, Un = /^[-+]0x[0-9a-f]+$/i, Xn = /^0b[01]+$/i, Wn = /^0o[0-7]+$/i, Gn = parseInt;
function Gt(e) {
  if (typeof e == "number")
    return e;
  if (gn(e))
    return Wt;
  if (St(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = St(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Vn(e);
  var r = Xn.test(e);
  return r || Wn.test(e) ? Gn(e.slice(2), r ? 2 : 8) : Un.test(e) ? Wt : +e;
}
var ut = function() {
  return hn.Date.now();
}, qn = "Expected a function", Kn = Math.max, Zn = Math.min;
function Qn(e, t, r) {
  var n, o, i, s, a, c, u = 0, p = !1, f = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(qn);
  t = Gt(t) || 0, St(r) && (p = !!r.leading, f = "maxWait" in r, i = f ? Kn(Gt(r.maxWait) || 0, t) : i, d = "trailing" in r ? !!r.trailing : d);
  function m(v) {
    var C = n, _ = o;
    return n = o = void 0, u = v, s = e.apply(_, C), s;
  }
  function b(v) {
    return u = v, a = setTimeout(h, t), p ? m(v) : s;
  }
  function y(v) {
    var C = v - c, _ = v - u, O = t - C;
    return f ? Zn(O, i - _) : O;
  }
  function g(v) {
    var C = v - c, _ = v - u;
    return c === void 0 || C >= t || C < 0 || f && _ >= i;
  }
  function h() {
    var v = ut();
    if (g(v))
      return E(v);
    a = setTimeout(h, y(v));
  }
  function E(v) {
    return a = void 0, d && n ? m(v) : (n = o = void 0, s);
  }
  function L() {
    a !== void 0 && clearTimeout(a), u = 0, n = c = o = a = void 0;
  }
  function S() {
    return a === void 0 ? s : E(ut());
  }
  function x() {
    var v = ut(), C = g(v);
    if (n = arguments, o = this, c = v, C) {
      if (a === void 0)
        return b(c);
      if (f)
        return clearTimeout(a), a = setTimeout(h, t), m(c);
    }
    return a === void 0 && (a = setTimeout(h, t)), s;
  }
  return x.cancel = L, x.flush = S, x;
}
var Pr = {
  exports: {}
}, Ue = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Yn = l, Jn = Symbol.for("react.element"), eo = Symbol.for("react.fragment"), to = Object.prototype.hasOwnProperty, ro = Yn.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, no = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Mr(e, t, r) {
  var n, o = {}, i = null, s = null;
  r !== void 0 && (i = "" + r), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) to.call(t, n) && !no.hasOwnProperty(n) && (o[n] = t[n]);
  if (e && e.defaultProps) for (n in t = e.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: Jn,
    type: e,
    key: i,
    ref: s,
    props: o,
    _owner: ro.current
  };
}
Ue.Fragment = eo;
Ue.jsx = Mr;
Ue.jsxs = Mr;
Pr.exports = Ue;
var X = Pr.exports;
const {
  SvelteComponent: oo,
  assign: qt,
  binding_callbacks: Kt,
  check_outros: io,
  children: Ir,
  claim_element: Or,
  claim_space: so,
  component_subscribe: Zt,
  compute_slots: ao,
  create_slot: lo,
  detach: pe,
  element: $r,
  empty: Qt,
  exclude_internal_props: Yt,
  get_all_dirty_from_scope: co,
  get_slot_changes: uo,
  group_outros: fo,
  init: po,
  insert_hydration: De,
  safe_not_equal: mo,
  set_custom_element_data: Ar,
  space: go,
  transition_in: Ne,
  transition_out: xt,
  update_slot_base: ho
} = window.__gradio__svelte__internal, {
  beforeUpdate: vo,
  getContext: bo,
  onDestroy: yo,
  setContext: So
} = window.__gradio__svelte__internal;
function Jt(e) {
  let t, r;
  const n = (
    /*#slots*/
    e[7].default
  ), o = lo(
    n,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = $r("svelte-slot"), o && o.c(), this.h();
    },
    l(i) {
      t = Or(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = Ir(t);
      o && o.l(s), s.forEach(pe), this.h();
    },
    h() {
      Ar(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      De(i, t, s), o && o.m(t, null), e[9](t), r = !0;
    },
    p(i, s) {
      o && o.p && (!r || s & /*$$scope*/
      64) && ho(
        o,
        n,
        i,
        /*$$scope*/
        i[6],
        r ? uo(
          n,
          /*$$scope*/
          i[6],
          s,
          null
        ) : co(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      r || (Ne(o, i), r = !0);
    },
    o(i) {
      xt(o, i), r = !1;
    },
    d(i) {
      i && pe(t), o && o.d(i), e[9](null);
    }
  };
}
function xo(e) {
  let t, r, n, o, i = (
    /*$$slots*/
    e[4].default && Jt(e)
  );
  return {
    c() {
      t = $r("react-portal-target"), r = go(), i && i.c(), n = Qt(), this.h();
    },
    l(s) {
      t = Or(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), Ir(t).forEach(pe), r = so(s), i && i.l(s), n = Qt(), this.h();
    },
    h() {
      Ar(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      De(s, t, a), e[8](t), De(s, r, a), i && i.m(s, a), De(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && Ne(i, 1)) : (i = Jt(s), i.c(), Ne(i, 1), i.m(n.parentNode, n)) : i && (fo(), xt(i, 1, 1, () => {
        i = null;
      }), io());
    },
    i(s) {
      o || (Ne(i), o = !0);
    },
    o(s) {
      xt(i), o = !1;
    },
    d(s) {
      s && (pe(t), pe(r), pe(n)), e[8](null), i && i.d(s);
    }
  };
}
function er(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function wo(e, t, r) {
  let n, o, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = ao(i);
  let {
    svelteInit: c
  } = t;
  const u = je(er(t)), p = je();
  Zt(e, p, (S) => r(0, n = S));
  const f = je();
  Zt(e, f, (S) => r(1, o = S));
  const d = [], m = bo("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: y,
    subSlotIndex: g
  } = vn() || {}, h = c({
    parent: m,
    props: u,
    target: p,
    slot: f,
    slotKey: b,
    slotIndex: y,
    subSlotIndex: g,
    onDestroy(S) {
      d.push(S);
    }
  });
  So("$$ms-gr-react-wrapper", h), vo(() => {
    u.set(er(t));
  }), yo(() => {
    d.forEach((S) => S());
  });
  function E(S) {
    Kt[S ? "unshift" : "push"](() => {
      n = S, p.set(n);
    });
  }
  function L(S) {
    Kt[S ? "unshift" : "push"](() => {
      o = S, f.set(o);
    });
  }
  return e.$$set = (S) => {
    r(17, t = qt(qt({}, t), Yt(S))), "svelteInit" in S && r(5, c = S.svelteInit), "$$scope" in S && r(6, s = S.$$scope);
  }, t = Yt(t), [n, o, p, f, a, c, s, i, E, L];
}
class Eo extends oo {
  constructor(t) {
    super(), po(this, t, wo, xo, mo, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ys
} = window.__gradio__svelte__internal, tr = window.ms_globals.rerender, ft = window.ms_globals.tree;
function Co(e, t = {}) {
  function r(n) {
    const o = je(), i = new Eo({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? ft;
          return c.nodes = [...c.nodes, a], tr({
            createPortal: ze,
            node: ft
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== o), tr({
              createPortal: ze,
              node: ft
            });
          }), a;
        },
        ...n.props
      }
    });
    return o.set(i), i;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise.then(() => {
      n(r);
    });
  });
}
const _o = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ro(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const n = e[r];
    return t[r] = To(r, n), t;
  }, {}) : {};
}
function To(e, t) {
  return typeof t == "number" && !_o.includes(e) ? t + "px" : t;
}
function wt(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const o = l.Children.toArray(e._reactElement.props.children).map((i) => {
      if (l.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = wt(i.props.el);
        return l.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...l.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(ze(l.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: s,
      type: a,
      useCapture: c
    }) => {
      r.addEventListener(a, s, c);
    });
  });
  const n = Array.from(e.childNodes);
  for (let o = 0; o < n.length; o++) {
    const i = n[o];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = wt(i);
      t.push(...a), r.appendChild(s);
    } else i.nodeType === 3 && r.appendChild(i.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Lo(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const we = un(({
  slot: e,
  clone: t,
  className: r,
  style: n,
  observeAttributes: o
}, i) => {
  const s = se(), [a, c] = fn([]), {
    forceClone: u
  } = yn(), p = u ? !0 : t;
  return xe(() => {
    var y;
    if (!s.current || !e)
      return;
    let f = e;
    function d() {
      let g = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (g = f.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Lo(i, g), r && g.classList.add(...r.split(" ")), n) {
        const h = Ro(n);
        Object.keys(h).forEach((E) => {
          g.style[E] = h[E];
        });
      }
    }
    let m = null, b = null;
    if (p && window.MutationObserver) {
      let g = function() {
        var S, x, v;
        (S = s.current) != null && S.contains(f) && ((x = s.current) == null || x.removeChild(f));
        const {
          portals: E,
          clonedElement: L
        } = wt(e);
        f = L, c(E), f.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          d();
        }, 50), (v = s.current) == null || v.appendChild(f);
      };
      g();
      const h = Qn(() => {
        g(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(h), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", d(), (y = s.current) == null || y.appendChild(f);
    return () => {
      var g, h;
      f.style.display = "", (g = s.current) != null && g.contains(f) && ((h = s.current) == null || h.removeChild(f)), m == null || m.disconnect();
    };
  }, [e, p, r, n, i, o, u]), l.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
});
function Po(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Mo(e, t = !1) {
  try {
    if (bn(e))
      return e;
    if (t && !Po(e))
      return;
    if (typeof e == "string") {
      let r = e.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function dt(e, t) {
  return Tr(() => Mo(e, t), [e, t]);
}
function Io(e, t) {
  return Object.keys(e).reduce((r, n) => (e[n] !== void 0 && (r[n] = e[n]), r), {});
}
const Oo = ({
  children: e,
  ...t
}) => /* @__PURE__ */ X.jsx(X.Fragment, {
  children: e(t)
});
function $o(e) {
  return l.createElement(Oo, {
    children: e
  });
}
function rr(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? $o((r) => /* @__PURE__ */ X.jsx(Sn, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ X.jsx(we, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ X.jsx(we, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function nr({
  key: e,
  slots: t,
  targets: r
}, n) {
  return t[e] ? (...o) => r ? r.map((i, s) => /* @__PURE__ */ X.jsx(l.Fragment, {
    children: rr(i, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ X.jsx(X.Fragment, {
    children: rr(t[e], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const Ao = "1.5.0";
function he() {
  return he = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var r = arguments[t];
      for (var n in r) ({}).hasOwnProperty.call(r, n) && (e[n] = r[n]);
    }
    return e;
  }, he.apply(null, arguments);
}
function B(e) {
  "@babel/helpers - typeof";
  return B = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, B(e);
}
function Fo(e, t) {
  if (B(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var n = r.call(e, t);
    if (B(n) != "object") return n;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Fr(e) {
  var t = Fo(e, "string");
  return B(t) == "symbol" ? t : t + "";
}
function T(e, t, r) {
  return (t = Fr(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function or(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var n = Object.getOwnPropertySymbols(e);
    t && (n = n.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), r.push.apply(r, n);
  }
  return r;
}
function R(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? or(Object(r), !0).forEach(function(n) {
      T(e, n, r[n]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : or(Object(r)).forEach(function(n) {
      Object.defineProperty(e, n, Object.getOwnPropertyDescriptor(r, n));
    });
  }
  return e;
}
const ko = /* @__PURE__ */ l.createContext({}), jo = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Do = (e) => {
  const t = l.useContext(ko);
  return l.useMemo(() => ({
    ...jo,
    ...t[e]
  }), [t[e]]);
};
function Be() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: n,
    theme: o
  } = l.useContext(xn.ConfigContext);
  return {
    theme: o,
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: n
  };
}
function No(e) {
  if (Array.isArray(e)) return e;
}
function zo(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var n, o, i, s, a = [], c = !0, u = !1;
    try {
      if (i = (r = r.call(e)).next, t === 0) {
        if (Object(r) !== r) return;
        c = !1;
      } else for (; !(c = (n = i.call(r)).done) && (a.push(n.value), a.length !== t); c = !0) ;
    } catch (p) {
      u = !0, o = p;
    } finally {
      try {
        if (!c && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (u) throw o;
      }
    }
    return a;
  }
}
function ir(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, n = Array(t); r < t; r++) n[r] = e[r];
  return n;
}
function Ho(e, t) {
  if (e) {
    if (typeof e == "string") return ir(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? ir(e, t) : void 0;
  }
}
function Bo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function W(e, t) {
  return No(e) || zo(e, t) || Ho(e, t) || Bo();
}
function be(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function sr(e, t) {
  for (var r = 0; r < t.length; r++) {
    var n = t[r];
    n.enumerable = n.enumerable || !1, n.configurable = !0, "value" in n && (n.writable = !0), Object.defineProperty(e, Fr(n.key), n);
  }
}
function ye(e, t, r) {
  return t && sr(e.prototype, t), r && sr(e, r), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function ue(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function Et(e, t) {
  return Et = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
    return r.__proto__ = n, r;
  }, Et(e, t);
}
function Xe(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && Et(e, t);
}
function Ve(e) {
  return Ve = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, Ve(e);
}
function kr() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (kr = function() {
    return !!e;
  })();
}
function Vo(e, t) {
  if (t && (B(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return ue(e);
}
function We(e) {
  var t = kr();
  return function() {
    var r, n = Ve(e);
    if (t) {
      var o = Ve(this).constructor;
      r = Reflect.construct(n, arguments, o);
    } else r = n.apply(this, arguments);
    return Vo(this, r);
  };
}
var jr = /* @__PURE__ */ ye(function e() {
  be(this, e);
}), Dr = "CALC_UNIT", Uo = new RegExp(Dr, "g");
function pt(e) {
  return typeof e == "number" ? "".concat(e).concat(Dr) : e;
}
var Xo = /* @__PURE__ */ function(e) {
  Xe(r, e);
  var t = We(r);
  function r(n, o) {
    var i;
    be(this, r), i = t.call(this), T(ue(i), "result", ""), T(ue(i), "unitlessCssVar", void 0), T(ue(i), "lowPriority", void 0);
    var s = B(n);
    return i.unitlessCssVar = o, n instanceof r ? i.result = "(".concat(n.result, ")") : s === "number" ? i.result = pt(n) : s === "string" && (i.result = n), i;
  }
  return ye(r, [{
    key: "add",
    value: function(o) {
      return o instanceof r ? this.result = "".concat(this.result, " + ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " + ").concat(pt(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof r ? this.result = "".concat(this.result, " - ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " - ").concat(pt(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof r ? this.result = "".concat(this.result, " * ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " * ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof r ? this.result = "".concat(this.result, " / ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " / ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(o) {
      return this.lowPriority || o ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(o) {
      var i = this, s = o || {}, a = s.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(u) {
        return i.result.includes(u);
      }) && (c = !1), this.result = this.result.replace(Uo, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), r;
}(jr), Wo = /* @__PURE__ */ function(e) {
  Xe(r, e);
  var t = We(r);
  function r(n) {
    var o;
    return be(this, r), o = t.call(this), T(ue(o), "result", 0), n instanceof r ? o.result = n.result : typeof n == "number" && (o.result = n), o;
  }
  return ye(r, [{
    key: "add",
    value: function(o) {
      return o instanceof r ? this.result += o.result : typeof o == "number" && (this.result += o), this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof r ? this.result -= o.result : typeof o == "number" && (this.result -= o), this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return o instanceof r ? this.result *= o.result : typeof o == "number" && (this.result *= o), this;
    }
  }, {
    key: "div",
    value: function(o) {
      return o instanceof r ? this.result /= o.result : typeof o == "number" && (this.result /= o), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), r;
}(jr), Go = function(t, r) {
  var n = t === "css" ? Xo : Wo;
  return function(o) {
    return new n(o, r);
  };
}, ar = function(t, r) {
  return "".concat([r, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ve(e) {
  var t = $.useRef();
  t.current = e;
  var r = $.useCallback(function() {
    for (var n, o = arguments.length, i = new Array(o), s = 0; s < o; s++)
      i[s] = arguments[s];
    return (n = t.current) === null || n === void 0 ? void 0 : n.call.apply(n, [t].concat(i));
  }, []);
  return r;
}
function Ge() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var lr = Ge() ? $.useLayoutEffect : $.useEffect, qo = function(t, r) {
  var n = $.useRef(!0);
  lr(function() {
    return t(n.current);
  }, r), lr(function() {
    return n.current = !1, function() {
      n.current = !0;
    };
  }, []);
}, cr = function(t, r) {
  qo(function(n) {
    if (!n)
      return t();
  }, r);
};
function Ee(e) {
  var t = $.useRef(!1), r = $.useState(e), n = W(r, 2), o = n[0], i = n[1];
  $.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, c) {
    c && t.current || i(a);
  }
  return [o, s];
}
function mt(e) {
  return e !== void 0;
}
function Ko(e, t) {
  var r = t || {}, n = r.defaultValue, o = r.value, i = r.onChange, s = r.postState, a = Ee(function() {
    return mt(o) ? o : mt(n) ? typeof n == "function" ? n() : n : typeof e == "function" ? e() : e;
  }), c = W(a, 2), u = c[0], p = c[1], f = o !== void 0 ? o : u, d = s ? s(f) : f, m = ve(i), b = Ee([f]), y = W(b, 2), g = y[0], h = y[1];
  cr(function() {
    var L = g[0];
    u !== L && m(u, L);
  }, [g]), cr(function() {
    mt(o) || p(o);
  }, [o]);
  var E = ve(function(L, S) {
    p(L, S), h([f], S);
  });
  return [d, E];
}
var Nr = {
  exports: {}
}, A = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ot = Symbol.for("react.element"), $t = Symbol.for("react.portal"), qe = Symbol.for("react.fragment"), Ke = Symbol.for("react.strict_mode"), Ze = Symbol.for("react.profiler"), Qe = Symbol.for("react.provider"), Ye = Symbol.for("react.context"), Zo = Symbol.for("react.server_context"), Je = Symbol.for("react.forward_ref"), et = Symbol.for("react.suspense"), tt = Symbol.for("react.suspense_list"), rt = Symbol.for("react.memo"), nt = Symbol.for("react.lazy"), Qo = Symbol.for("react.offscreen"), zr;
zr = Symbol.for("react.module.reference");
function Y(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Ot:
        switch (e = e.type, e) {
          case qe:
          case Ze:
          case Ke:
          case et:
          case tt:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Zo:
              case Ye:
              case Je:
              case nt:
              case rt:
              case Qe:
                return e;
              default:
                return t;
            }
        }
      case $t:
        return t;
    }
  }
}
A.ContextConsumer = Ye;
A.ContextProvider = Qe;
A.Element = Ot;
A.ForwardRef = Je;
A.Fragment = qe;
A.Lazy = nt;
A.Memo = rt;
A.Portal = $t;
A.Profiler = Ze;
A.StrictMode = Ke;
A.Suspense = et;
A.SuspenseList = tt;
A.isAsyncMode = function() {
  return !1;
};
A.isConcurrentMode = function() {
  return !1;
};
A.isContextConsumer = function(e) {
  return Y(e) === Ye;
};
A.isContextProvider = function(e) {
  return Y(e) === Qe;
};
A.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Ot;
};
A.isForwardRef = function(e) {
  return Y(e) === Je;
};
A.isFragment = function(e) {
  return Y(e) === qe;
};
A.isLazy = function(e) {
  return Y(e) === nt;
};
A.isMemo = function(e) {
  return Y(e) === rt;
};
A.isPortal = function(e) {
  return Y(e) === $t;
};
A.isProfiler = function(e) {
  return Y(e) === Ze;
};
A.isStrictMode = function(e) {
  return Y(e) === Ke;
};
A.isSuspense = function(e) {
  return Y(e) === et;
};
A.isSuspenseList = function(e) {
  return Y(e) === tt;
};
A.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === qe || e === Ze || e === Ke || e === et || e === tt || e === Qo || typeof e == "object" && e !== null && (e.$$typeof === nt || e.$$typeof === rt || e.$$typeof === Qe || e.$$typeof === Ye || e.$$typeof === Je || e.$$typeof === zr || e.getModuleId !== void 0);
};
A.typeOf = Y;
Nr.exports = A;
var gt = Nr.exports, Yo = Symbol.for("react.element"), Jo = Symbol.for("react.transitional.element"), ei = Symbol.for("react.fragment");
function ti(e) {
  return (
    // Base object type
    e && B(e) === "object" && // React Element type
    (e.$$typeof === Yo || e.$$typeof === Jo) && // React Fragment type
    e.type === ei
  );
}
var ri = Number(dn.split(".")[0]), ni = function(t, r) {
  typeof t == "function" ? t(r) : B(t) === "object" && t && "current" in t && (t.current = r);
}, oi = function(t) {
  var r, n;
  if (!t)
    return !1;
  if (Hr(t) && ri >= 19)
    return !0;
  var o = gt.isMemo(t) ? t.type.type : t.type;
  return !(typeof o == "function" && !((r = o.prototype) !== null && r !== void 0 && r.render) && o.$$typeof !== gt.ForwardRef || typeof t == "function" && !((n = t.prototype) !== null && n !== void 0 && n.render) && t.$$typeof !== gt.ForwardRef);
};
function Hr(e) {
  return /* @__PURE__ */ pn(e) && !ti(e);
}
var ii = function(t) {
  if (t && Hr(t)) {
    var r = t;
    return r.props.propertyIsEnumerable("ref") ? r.props.ref : r.ref;
  }
  return null;
};
function ur(e, t, r, n) {
  var o = R({}, t[e]);
  if (n != null && n.deprecatedTokens) {
    var i = n.deprecatedTokens;
    i.forEach(function(a) {
      var c = W(a, 2), u = c[0], p = c[1];
      if (o != null && o[u] || o != null && o[p]) {
        var f;
        (f = o[p]) !== null && f !== void 0 || (o[p] = o == null ? void 0 : o[u]);
      }
    });
  }
  var s = R(R({}, r), o);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Br = typeof CSSINJS_STATISTIC < "u", Ct = !0;
function At() {
  for (var e = arguments.length, t = new Array(e), r = 0; r < e; r++)
    t[r] = arguments[r];
  if (!Br)
    return Object.assign.apply(Object, [{}].concat(t));
  Ct = !1;
  var n = {};
  return t.forEach(function(o) {
    if (B(o) === "object") {
      var i = Object.keys(o);
      i.forEach(function(s) {
        Object.defineProperty(n, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return o[s];
          }
        });
      });
    }
  }), Ct = !0, n;
}
var fr = {};
function si() {
}
var ai = function(t) {
  var r, n = t, o = si;
  return Br && typeof Proxy < "u" && (r = /* @__PURE__ */ new Set(), n = new Proxy(t, {
    get: function(s, a) {
      if (Ct) {
        var c;
        (c = r) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), o = function(s, a) {
    var c;
    fr[s] = {
      global: Array.from(r),
      component: R(R({}, (c = fr[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: n,
    keys: r,
    flush: o
  };
};
function dr(e, t, r) {
  if (typeof r == "function") {
    var n;
    return r(At(t, (n = t[e]) !== null && n !== void 0 ? n : {}));
  }
  return r ?? {};
}
function li(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var r = arguments.length, n = new Array(r), o = 0; o < r; o++)
        n[o] = arguments[o];
      return "max(".concat(n.map(function(i) {
        return Ut(i);
      }).join(","), ")");
    },
    min: function() {
      for (var r = arguments.length, n = new Array(r), o = 0; o < r; o++)
        n[o] = arguments[o];
      return "min(".concat(n.map(function(i) {
        return Ut(i);
      }).join(","), ")");
    }
  };
}
var ci = 1e3 * 60 * 10, ui = /* @__PURE__ */ function() {
  function e() {
    be(this, e), T(this, "map", /* @__PURE__ */ new Map()), T(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), T(this, "nextID", 0), T(this, "lastAccessBeat", /* @__PURE__ */ new Map()), T(this, "accessBeat", 0);
  }
  return ye(e, [{
    key: "set",
    value: function(r, n) {
      this.clear();
      var o = this.getCompositeKey(r);
      this.map.set(o, n), this.lastAccessBeat.set(o, Date.now());
    }
  }, {
    key: "get",
    value: function(r) {
      var n = this.getCompositeKey(r), o = this.map.get(n);
      return this.lastAccessBeat.set(n, Date.now()), this.accessBeat += 1, o;
    }
  }, {
    key: "getCompositeKey",
    value: function(r) {
      var n = this, o = r.map(function(i) {
        return i && B(i) === "object" ? "obj_".concat(n.getObjectID(i)) : "".concat(B(i), "_").concat(i);
      });
      return o.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(r) {
      if (this.objectIDMap.has(r))
        return this.objectIDMap.get(r);
      var n = this.nextID;
      return this.objectIDMap.set(r, n), this.nextID += 1, n;
    }
  }, {
    key: "clear",
    value: function() {
      var r = this;
      if (this.accessBeat > 1e4) {
        var n = Date.now();
        this.lastAccessBeat.forEach(function(o, i) {
          n - o > ci && (r.map.delete(i), r.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), pr = new ui();
function fi(e, t) {
  return l.useMemo(function() {
    var r = pr.get(t);
    if (r)
      return r;
    var n = e();
    return pr.set(t, n), n;
  }, t);
}
var di = function() {
  return {};
};
function pi(e) {
  var t = e.useCSP, r = t === void 0 ? di : t, n = e.useToken, o = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function c(d, m, b, y) {
    var g = Array.isArray(d) ? d[0] : d;
    function h(_) {
      return "".concat(String(g)).concat(_.slice(0, 1).toUpperCase()).concat(_.slice(1));
    }
    var E = (y == null ? void 0 : y.unitless) || {}, L = typeof a == "function" ? a(d) : {}, S = R(R({}, L), {}, T({}, h("zIndexPopup"), !0));
    Object.keys(E).forEach(function(_) {
      S[h(_)] = E[_];
    });
    var x = R(R({}, y), {}, {
      unitless: S,
      prefixToken: h
    }), v = p(d, m, b, x), C = u(g, b, x);
    return function(_) {
      var O = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : _, w = v(_, O), M = W(w, 2), P = M[1], I = C(O), F = W(I, 2), k = F[0], j = F[1];
      return [k, P, j];
    };
  }
  function u(d, m, b) {
    var y = b.unitless, g = b.injectStyle, h = g === void 0 ? !0 : g, E = b.prefixToken, L = b.ignore, S = function(C) {
      var _ = C.rootCls, O = C.cssVar, w = O === void 0 ? {} : O, M = n(), P = M.realToken;
      return jn({
        path: [d],
        prefix: w.prefix,
        key: w.key,
        unitless: y,
        ignore: L,
        token: P,
        scope: _
      }, function() {
        var I = dr(d, P, m), F = ur(d, P, I, {
          deprecatedTokens: b == null ? void 0 : b.deprecatedTokens
        });
        return Object.keys(I).forEach(function(k) {
          F[E(k)] = F[k], delete F[k];
        }), F;
      }), null;
    }, x = function(C) {
      var _ = n(), O = _.cssVar;
      return [function(w) {
        return h && O ? /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(S, {
          rootCls: C,
          cssVar: O,
          component: d
        }), w) : w;
      }, O == null ? void 0 : O.key];
    };
    return x;
  }
  function p(d, m, b) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(d) ? d : [d, d], h = W(g, 1), E = h[0], L = g.join("-"), S = e.layer || {
      name: "antd"
    };
    return function(x) {
      var v = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : x, C = n(), _ = C.theme, O = C.realToken, w = C.hashId, M = C.token, P = C.cssVar, I = o(), F = I.rootPrefixCls, k = I.iconPrefixCls, j = r(), z = P ? "css" : "js", q = fi(function() {
        var N = /* @__PURE__ */ new Set();
        return P && Object.keys(y.unitless || {}).forEach(function(K) {
          N.add(ct(K, P.prefix)), N.add(ct(K, ar(E, P.prefix)));
        }), Go(z, N);
      }, [z, E, P == null ? void 0 : P.prefix]), fe = li(z), oe = fe.max, V = fe.min, D = {
        theme: _,
        token: M,
        hashId: w,
        nonce: function() {
          return j.nonce;
        },
        clientOnly: y.clientOnly,
        layer: S,
        // antd is always at top of styles
        order: y.order || -999
      };
      typeof i == "function" && Xt(R(R({}, D), {}, {
        clientOnly: !1,
        path: ["Shared", F]
      }), function() {
        return i(M, {
          prefix: {
            rootPrefixCls: F,
            iconPrefixCls: k
          },
          csp: j
        });
      });
      var G = Xt(R(R({}, D), {}, {
        path: [L, x, k]
      }), function() {
        if (y.injectStyle === !1)
          return [];
        var N = ai(M), K = N.token, ae = N.flush, re = dr(E, O, b), ot = ".".concat(x), _e = ur(E, O, re, {
          deprecatedTokens: y.deprecatedTokens
        });
        P && re && B(re) === "object" && Object.keys(re).forEach(function(Le) {
          re[Le] = "var(".concat(ct(Le, ar(E, P.prefix)), ")");
        });
        var Re = At(K, {
          componentCls: ot,
          prefixCls: x,
          iconCls: ".".concat(k),
          antCls: ".".concat(F),
          calc: q,
          // @ts-ignore
          max: oe,
          // @ts-ignore
          min: V
        }, P ? re : _e), Te = m(Re, {
          hashId: w,
          prefixCls: x,
          rootPrefixCls: F,
          iconPrefixCls: k
        });
        ae(E, _e);
        var le = typeof s == "function" ? s(Re, x, v, y.resetFont) : null;
        return [y.resetStyle === !1 ? null : le, Te];
      });
      return [G, w];
    };
  }
  function f(d, m, b) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = p(d, m, b, R({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, y)), h = function(L) {
      var S = L.prefixCls, x = L.rootCls, v = x === void 0 ? S : x;
      return g(S, v), null;
    };
    return h;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: f,
    genComponentStyleHook: p
  };
}
const mi = {
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
}, gi = Object.assign(Object.assign({}, mi), {
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
}), H = Math.round;
function ht(e, t) {
  const r = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], n = r.map((o) => parseFloat(o));
  for (let o = 0; o < 3; o += 1)
    n[o] = t(n[o] || 0, r[o] || "", o);
  return r[3] ? n[3] = r[3].includes("%") ? n[3] / 100 : n[3] : n[3] = 1, n;
}
const mr = (e, t, r) => r === 0 ? e : e / 100;
function Se(e, t) {
  const r = t || 255;
  return e > r ? r : e < 0 ? 0 : e;
}
class te {
  constructor(t) {
    T(this, "isValid", !0), T(this, "r", 0), T(this, "g", 0), T(this, "b", 0), T(this, "a", 1), T(this, "_h", void 0), T(this, "_s", void 0), T(this, "_l", void 0), T(this, "_v", void 0), T(this, "_max", void 0), T(this, "_min", void 0), T(this, "_brightness", void 0);
    function r(n) {
      return n[0] in t && n[1] in t && n[2] in t;
    }
    if (t) if (typeof t == "string") {
      let o = function(i) {
        return n.startsWith(i);
      };
      const n = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(n) ? this.fromHexString(n) : o("rgb") ? this.fromRgbString(n) : o("hsl") ? this.fromHslString(n) : (o("hsv") || o("hsb")) && this.fromHsvString(n);
    } else if (t instanceof te)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (r("rgb"))
      this.r = Se(t.r), this.g = Se(t.g), this.b = Se(t.b), this.a = typeof t.a == "number" ? Se(t.a, 1) : 1;
    else if (r("hsl"))
      this.fromHsl(t);
    else if (r("hsv"))
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
    const r = this.toHsv();
    return r.h = t, this._c(r);
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
    const r = t(this.r), n = t(this.g), o = t(this.b);
    return 0.2126 * r + 0.7152 * n + 0.0722 * o;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = H(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const r = this.getHue(), n = this.getSaturation();
    let o = this.getLightness() - t / 100;
    return o < 0 && (o = 0), this._c({
      h: r,
      s: n,
      l: o,
      a: this.a
    });
  }
  lighten(t = 10) {
    const r = this.getHue(), n = this.getSaturation();
    let o = this.getLightness() + t / 100;
    return o > 1 && (o = 1), this._c({
      h: r,
      s: n,
      l: o,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, r = 50) {
    const n = this._c(t), o = r / 100, i = (a) => (n[a] - this[a]) * o + this[a], s = {
      r: H(i("r")),
      g: H(i("g")),
      b: H(i("b")),
      a: H(i("a") * 100) / 100
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
    const r = this._c(t), n = this.a + r.a * (1 - this.a), o = (i) => H((this[i] * this.a + r[i] * r.a * (1 - this.a)) / n);
    return this._c({
      r: o("r"),
      g: o("g"),
      b: o("b"),
      a: n
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
    const r = (this.r || 0).toString(16);
    t += r.length === 2 ? r : "0" + r;
    const n = (this.g || 0).toString(16);
    t += n.length === 2 ? n : "0" + n;
    const o = (this.b || 0).toString(16);
    if (t += o.length === 2 ? o : "0" + o, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = H(this.a * 255).toString(16);
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
    const t = this.getHue(), r = H(this.getSaturation() * 100), n = H(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${r}%,${n}%,${this.a})` : `hsl(${t},${r}%,${n}%)`;
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
  _sc(t, r, n) {
    const o = this.clone();
    return o[t] = Se(r, n), o;
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
    const r = t.replace("#", "");
    function n(o, i) {
      return parseInt(r[o] + r[i || o], 16);
    }
    r.length < 6 ? (this.r = n(0), this.g = n(1), this.b = n(2), this.a = r[3] ? n(3) / 255 : 1) : (this.r = n(0, 1), this.g = n(2, 3), this.b = n(4, 5), this.a = r[6] ? n(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: r,
    l: n,
    a: o
  }) {
    if (this._h = t % 360, this._s = r, this._l = n, this.a = typeof o == "number" ? o : 1, r <= 0) {
      const d = H(n * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const c = t / 60, u = (1 - Math.abs(2 * n - 1)) * r, p = u * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = u, s = p) : c >= 1 && c < 2 ? (i = p, s = u) : c >= 2 && c < 3 ? (s = u, a = p) : c >= 3 && c < 4 ? (s = p, a = u) : c >= 4 && c < 5 ? (i = p, a = u) : c >= 5 && c < 6 && (i = u, a = p);
    const f = n - u / 2;
    this.r = H((i + f) * 255), this.g = H((s + f) * 255), this.b = H((a + f) * 255);
  }
  fromHsv({
    h: t,
    s: r,
    v: n,
    a: o
  }) {
    this._h = t % 360, this._s = r, this._v = n, this.a = typeof o == "number" ? o : 1;
    const i = H(n * 255);
    if (this.r = i, this.g = i, this.b = i, r <= 0)
      return;
    const s = t / 60, a = Math.floor(s), c = s - a, u = H(n * (1 - r) * 255), p = H(n * (1 - r * c) * 255), f = H(n * (1 - r * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = f, this.b = u;
        break;
      case 1:
        this.r = p, this.b = u;
        break;
      case 2:
        this.r = u, this.b = f;
        break;
      case 3:
        this.r = u, this.g = p;
        break;
      case 4:
        this.r = f, this.g = u;
        break;
      case 5:
      default:
        this.g = u, this.b = p;
        break;
    }
  }
  fromHsvString(t) {
    const r = ht(t, mr);
    this.fromHsv({
      h: r[0],
      s: r[1],
      v: r[2],
      a: r[3]
    });
  }
  fromHslString(t) {
    const r = ht(t, mr);
    this.fromHsl({
      h: r[0],
      s: r[1],
      l: r[2],
      a: r[3]
    });
  }
  fromRgbString(t) {
    const r = ht(t, (n, o) => (
      // Convert percentage to number. e.g. 50% -> 128
      o.includes("%") ? H(n / 100 * 255) : n
    ));
    this.r = r[0], this.g = r[1], this.b = r[2], this.a = r[3];
  }
}
function vt(e) {
  return e >= 0 && e <= 255;
}
function Ie(e, t) {
  const {
    r,
    g: n,
    b: o,
    a: i
  } = new te(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: c
  } = new te(t).toRgb();
  for (let u = 0.01; u <= 1; u += 0.01) {
    const p = Math.round((r - s * (1 - u)) / u), f = Math.round((n - a * (1 - u)) / u), d = Math.round((o - c * (1 - u)) / u);
    if (vt(p) && vt(f) && vt(d))
      return new te({
        r: p,
        g: f,
        b: d,
        a: Math.round(u * 100) / 100
      }).toRgbString();
  }
  return new te({
    r,
    g: n,
    b: o,
    a: 1
  }).toRgbString();
}
var hi = function(e, t) {
  var r = {};
  for (var n in e) Object.prototype.hasOwnProperty.call(e, n) && t.indexOf(n) < 0 && (r[n] = e[n]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var o = 0, n = Object.getOwnPropertySymbols(e); o < n.length; o++)
    t.indexOf(n[o]) < 0 && Object.prototype.propertyIsEnumerable.call(e, n[o]) && (r[n[o]] = e[n[o]]);
  return r;
};
function vi(e) {
  const {
    override: t
  } = e, r = hi(e, ["override"]), n = Object.assign({}, t);
  Object.keys(gi).forEach((d) => {
    delete n[d];
  });
  const o = Object.assign(Object.assign({}, r), n), i = 480, s = 576, a = 768, c = 992, u = 1200, p = 1600;
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
    colorSplit: Ie(o.colorBorderSecondary, o.colorBgContainer),
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
    colorErrorOutline: Ie(o.colorErrorBg, o.colorBgContainer),
    colorWarningOutline: Ie(o.colorWarningBg, o.colorBgContainer),
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
    controlOutline: Ie(o.colorPrimaryBg, o.colorBgContainer),
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
      0 1px 2px -2px ${new te("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new te("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new te("rgba(0, 0, 0, 0.09)").toRgbString()}
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
  }), n);
}
const bi = {
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
}, yi = {
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
}, Si = Dn(He.defaultAlgorithm), xi = {
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
}, Vr = (e, t, r) => {
  const n = r.getDerivativeToken(e), {
    override: o,
    ...i
  } = t;
  let s = {
    ...n,
    override: o
  };
  return s = vi(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: u,
      ...p
    } = c;
    let f = p;
    u && (f = Vr({
      ...s,
      ...p
    }, {
      override: p
    }, u)), s[a] = f;
  }), s;
};
function wi() {
  const {
    token: e,
    hashed: t,
    theme: r = Si,
    override: n,
    cssVar: o
  } = l.useContext(He._internalContext), [i, s, a] = Nn(r, [He.defaultSeed, e], {
    salt: `${Ao}-${t || ""}`,
    override: n,
    getComputedToken: Vr,
    cssVar: o && {
      prefix: o.prefix,
      key: o.key,
      unitless: bi,
      ignore: yi,
      preserve: xi
    }
  });
  return [r, a, t ? s : "", i, o];
}
const {
  genStyleHooks: Ei
} = pi({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Be();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, r, n, o] = wi();
    return {
      theme: e,
      realToken: t,
      hashId: r,
      token: n,
      cssVar: o
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = Be();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), Ce = /* @__PURE__ */ l.createContext(null);
function gr(e) {
  const {
    getDropContainer: t,
    className: r,
    prefixCls: n,
    children: o
  } = e, {
    disabled: i
  } = l.useContext(Ce), [s, a] = l.useState(), [c, u] = l.useState(null);
  if (l.useEffect(() => {
    const d = t == null ? void 0 : t();
    s !== d && a(d);
  }, [t]), l.useEffect(() => {
    if (s) {
      const d = () => {
        u(!0);
      }, m = (g) => {
        g.preventDefault();
      }, b = (g) => {
        g.relatedTarget || u(!1);
      }, y = (g) => {
        u(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", d), document.addEventListener("dragover", m), document.addEventListener("dragleave", b), document.addEventListener("drop", y), () => {
        document.removeEventListener("dragenter", d), document.removeEventListener("dragover", m), document.removeEventListener("dragleave", b), document.removeEventListener("drop", y);
      };
    }
  }, [!!s]), !(t && s && !i))
    return null;
  const f = `${n}-drop-area`;
  return /* @__PURE__ */ ze(/* @__PURE__ */ l.createElement("div", {
    className: Q(f, r, {
      [`${f}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: c ? "block" : "none"
    }
  }, o), s);
}
function hr(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function Ci(e) {
  return e && B(e) === "object" && hr(e.nativeElement) ? e.nativeElement : hr(e) ? e : null;
}
function _i(e) {
  var t = Ci(e);
  if (t)
    return t;
  if (e instanceof l.Component) {
    var r;
    return (r = Vt.findDOMNode) === null || r === void 0 ? void 0 : r.call(Vt, e);
  }
  return null;
}
function Ri(e, t) {
  if (e == null) return {};
  var r = {};
  for (var n in e) if ({}.hasOwnProperty.call(e, n)) {
    if (t.indexOf(n) !== -1) continue;
    r[n] = e[n];
  }
  return r;
}
function vr(e, t) {
  if (e == null) return {};
  var r, n, o = Ri(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (n = 0; n < i.length; n++) r = i[n], t.indexOf(r) === -1 && {}.propertyIsEnumerable.call(e, r) && (o[r] = e[r]);
  }
  return o;
}
var Ti = /* @__PURE__ */ $.createContext({}), Li = /* @__PURE__ */ function(e) {
  Xe(r, e);
  var t = We(r);
  function r() {
    return be(this, r), t.apply(this, arguments);
  }
  return ye(r, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), r;
}($.Component);
function Pi(e) {
  var t = $.useReducer(function(a) {
    return a + 1;
  }, 0), r = W(t, 2), n = r[1], o = $.useRef(e), i = ve(function() {
    return o.current;
  }), s = ve(function(a) {
    o.current = typeof a == "function" ? a(o.current) : a, n();
  });
  return [i, s];
}
var ie = "none", Oe = "appear", $e = "enter", Ae = "leave", br = "none", J = "prepare", me = "start", ge = "active", Ft = "end", Ur = "prepared";
function yr(e, t) {
  var r = {};
  return r[e.toLowerCase()] = t.toLowerCase(), r["Webkit".concat(e)] = "webkit".concat(t), r["Moz".concat(e)] = "moz".concat(t), r["ms".concat(e)] = "MS".concat(t), r["O".concat(e)] = "o".concat(t.toLowerCase()), r;
}
function Mi(e, t) {
  var r = {
    animationend: yr("Animation", "AnimationEnd"),
    transitionend: yr("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete r.animationend.animation, "TransitionEvent" in t || delete r.transitionend.transition), r;
}
var Ii = Mi(Ge(), typeof window < "u" ? window : {}), Xr = {};
if (Ge()) {
  var Oi = document.createElement("div");
  Xr = Oi.style;
}
var Fe = {};
function Wr(e) {
  if (Fe[e])
    return Fe[e];
  var t = Ii[e];
  if (t)
    for (var r = Object.keys(t), n = r.length, o = 0; o < n; o += 1) {
      var i = r[o];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in Xr)
        return Fe[e] = t[i], Fe[e];
    }
  return "";
}
var Gr = Wr("animationend"), qr = Wr("transitionend"), Kr = !!(Gr && qr), Sr = Gr || "animationend", xr = qr || "transitionend";
function wr(e, t) {
  if (!e) return null;
  if (B(e) === "object") {
    var r = t.replace(/-\w/g, function(n) {
      return n[1].toUpperCase();
    });
    return e[r];
  }
  return "".concat(e, "-").concat(t);
}
const $i = function(e) {
  var t = se();
  function r(o) {
    o && (o.removeEventListener(xr, e), o.removeEventListener(Sr, e));
  }
  function n(o) {
    t.current && t.current !== o && r(t.current), o && o !== t.current && (o.addEventListener(xr, e), o.addEventListener(Sr, e), t.current = o);
  }
  return $.useEffect(function() {
    return function() {
      r(t.current);
    };
  }, []), [n, r];
};
var Zr = Ge() ? mn : xe, Qr = function(t) {
  return +setTimeout(t, 16);
}, Yr = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Qr = function(t) {
  return window.requestAnimationFrame(t);
}, Yr = function(t) {
  return window.cancelAnimationFrame(t);
});
var Er = 0, kt = /* @__PURE__ */ new Map();
function Jr(e) {
  kt.delete(e);
}
var _t = function(t) {
  var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  Er += 1;
  var n = Er;
  function o(i) {
    if (i === 0)
      Jr(n), t();
    else {
      var s = Qr(function() {
        o(i - 1);
      });
      kt.set(n, s);
    }
  }
  return o(r), n;
};
_t.cancel = function(e) {
  var t = kt.get(e);
  return Jr(e), Yr(t);
};
const Ai = function() {
  var e = $.useRef(null);
  function t() {
    _t.cancel(e.current);
  }
  function r(n) {
    var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = _t(function() {
      o <= 1 ? n({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : r(n, o - 1);
    });
    e.current = i;
  }
  return $.useEffect(function() {
    return function() {
      t();
    };
  }, []), [r, t];
};
var Fi = [J, me, ge, Ft], ki = [J, Ur], en = !1, ji = !0;
function tn(e) {
  return e === ge || e === Ft;
}
const Di = function(e, t, r) {
  var n = Ee(br), o = W(n, 2), i = o[0], s = o[1], a = Ai(), c = W(a, 2), u = c[0], p = c[1];
  function f() {
    s(J, !0);
  }
  var d = t ? ki : Fi;
  return Zr(function() {
    if (i !== br && i !== Ft) {
      var m = d.indexOf(i), b = d[m + 1], y = r(i);
      y === en ? s(b, !0) : b && u(function(g) {
        function h() {
          g.isCanceled() || s(b, !0);
        }
        y === !0 ? h() : Promise.resolve(y).then(h);
      });
    }
  }, [e, i]), $.useEffect(function() {
    return function() {
      p();
    };
  }, []), [f, i];
};
function Ni(e, t, r, n) {
  var o = n.motionEnter, i = o === void 0 ? !0 : o, s = n.motionAppear, a = s === void 0 ? !0 : s, c = n.motionLeave, u = c === void 0 ? !0 : c, p = n.motionDeadline, f = n.motionLeaveImmediately, d = n.onAppearPrepare, m = n.onEnterPrepare, b = n.onLeavePrepare, y = n.onAppearStart, g = n.onEnterStart, h = n.onLeaveStart, E = n.onAppearActive, L = n.onEnterActive, S = n.onLeaveActive, x = n.onAppearEnd, v = n.onEnterEnd, C = n.onLeaveEnd, _ = n.onVisibleChanged, O = Ee(), w = W(O, 2), M = w[0], P = w[1], I = Pi(ie), F = W(I, 2), k = F[0], j = F[1], z = Ee(null), q = W(z, 2), fe = q[0], oe = q[1], V = k(), D = se(!1), G = se(null);
  function N() {
    return r();
  }
  var K = se(!1);
  function ae() {
    j(ie), oe(null, !0);
  }
  var re = ve(function(Z) {
    var U = k();
    if (U !== ie) {
      var ee = N();
      if (!(Z && !Z.deadline && Z.target !== ee)) {
        var Pe = K.current, Me;
        U === Oe && Pe ? Me = x == null ? void 0 : x(ee, Z) : U === $e && Pe ? Me = v == null ? void 0 : v(ee, Z) : U === Ae && Pe && (Me = C == null ? void 0 : C(ee, Z)), Pe && Me !== !1 && ae();
      }
    }
  }), ot = $i(re), _e = W(ot, 1), Re = _e[0], Te = function(U) {
    switch (U) {
      case Oe:
        return T(T(T({}, J, d), me, y), ge, E);
      case $e:
        return T(T(T({}, J, m), me, g), ge, L);
      case Ae:
        return T(T(T({}, J, b), me, h), ge, S);
      default:
        return {};
    }
  }, le = $.useMemo(function() {
    return Te(V);
  }, [V]), Le = Di(V, !e, function(Z) {
    if (Z === J) {
      var U = le[J];
      return U ? U(N()) : en;
    }
    if (ce in le) {
      var ee;
      oe(((ee = le[ce]) === null || ee === void 0 ? void 0 : ee.call(le, N(), null)) || null);
    }
    return ce === ge && V !== ie && (Re(N()), p > 0 && (clearTimeout(G.current), G.current = setTimeout(function() {
      re({
        deadline: !0
      });
    }, p))), ce === Ur && ae(), ji;
  }), jt = W(Le, 2), ln = jt[0], ce = jt[1], cn = tn(ce);
  K.current = cn;
  var Dt = se(null);
  Zr(function() {
    if (!(D.current && Dt.current === t)) {
      P(t);
      var Z = D.current;
      D.current = !0;
      var U;
      !Z && t && a && (U = Oe), Z && t && i && (U = $e), (Z && !t && u || !Z && f && !t && u) && (U = Ae);
      var ee = Te(U);
      U && (e || ee[J]) ? (j(U), ln()) : j(ie), Dt.current = t;
    }
  }, [t]), xe(function() {
    // Cancel appear
    (V === Oe && !a || // Cancel enter
    V === $e && !i || // Cancel leave
    V === Ae && !u) && j(ie);
  }, [a, i, u]), xe(function() {
    return function() {
      D.current = !1, clearTimeout(G.current);
    };
  }, []);
  var it = $.useRef(!1);
  xe(function() {
    M && (it.current = !0), M !== void 0 && V === ie && ((it.current || M) && (_ == null || _(M)), it.current = !0);
  }, [M, V]);
  var st = fe;
  return le[J] && ce === me && (st = R({
    transition: "none"
  }, st)), [V, ce, st, M ?? t];
}
function zi(e) {
  var t = e;
  B(e) === "object" && (t = e.transitionSupport);
  function r(o, i) {
    return !!(o.motionName && t && i !== !1);
  }
  var n = /* @__PURE__ */ $.forwardRef(function(o, i) {
    var s = o.visible, a = s === void 0 ? !0 : s, c = o.removeOnLeave, u = c === void 0 ? !0 : c, p = o.forceRender, f = o.children, d = o.motionName, m = o.leavedClassName, b = o.eventProps, y = $.useContext(Ti), g = y.motion, h = r(o, g), E = se(), L = se();
    function S() {
      try {
        return E.current instanceof HTMLElement ? E.current : _i(L.current);
      } catch {
        return null;
      }
    }
    var x = Ni(h, a, S, o), v = W(x, 4), C = v[0], _ = v[1], O = v[2], w = v[3], M = $.useRef(w);
    w && (M.current = !0);
    var P = $.useCallback(function(q) {
      E.current = q, ni(i, q);
    }, [i]), I, F = R(R({}, b), {}, {
      visible: a
    });
    if (!f)
      I = null;
    else if (C === ie)
      w ? I = f(R({}, F), P) : !u && M.current && m ? I = f(R(R({}, F), {}, {
        className: m
      }), P) : p || !u && !m ? I = f(R(R({}, F), {}, {
        style: {
          display: "none"
        }
      }), P) : I = null;
    else {
      var k;
      _ === J ? k = "prepare" : tn(_) ? k = "active" : _ === me && (k = "start");
      var j = wr(d, "".concat(C, "-").concat(k));
      I = f(R(R({}, F), {}, {
        className: Q(wr(d, C), T(T({}, j, j && k), d, typeof d == "string")),
        style: O
      }), P);
    }
    if (/* @__PURE__ */ $.isValidElement(I) && oi(I)) {
      var z = ii(I);
      z || (I = /* @__PURE__ */ $.cloneElement(I, {
        ref: P
      }));
    }
    return /* @__PURE__ */ $.createElement(Li, {
      ref: L
    }, I);
  });
  return n.displayName = "CSSMotion", n;
}
const Hi = zi(Kr);
var Rt = "add", Tt = "keep", Lt = "remove", bt = "removed";
function Bi(e) {
  var t;
  return e && B(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, R(R({}, t), {}, {
    key: String(t.key)
  });
}
function Pt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(Bi);
}
function Vi() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], r = [], n = 0, o = t.length, i = Pt(e), s = Pt(t);
  i.forEach(function(u) {
    for (var p = !1, f = n; f < o; f += 1) {
      var d = s[f];
      if (d.key === u.key) {
        n < f && (r = r.concat(s.slice(n, f).map(function(m) {
          return R(R({}, m), {}, {
            status: Rt
          });
        })), n = f), r.push(R(R({}, d), {}, {
          status: Tt
        })), n += 1, p = !0;
        break;
      }
    }
    p || r.push(R(R({}, u), {}, {
      status: Lt
    }));
  }), n < o && (r = r.concat(s.slice(n).map(function(u) {
    return R(R({}, u), {}, {
      status: Rt
    });
  })));
  var a = {};
  r.forEach(function(u) {
    var p = u.key;
    a[p] = (a[p] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(u) {
    return a[u] > 1;
  });
  return c.forEach(function(u) {
    r = r.filter(function(p) {
      var f = p.key, d = p.status;
      return f !== u || d !== Lt;
    }), r.forEach(function(p) {
      p.key === u && (p.status = Tt);
    });
  }), r;
}
var Ui = ["component", "children", "onVisibleChanged", "onAllRemoved"], Xi = ["status"], Wi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function Gi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Hi, r = /* @__PURE__ */ function(n) {
    Xe(i, n);
    var o = We(i);
    function i() {
      var s;
      be(this, i);
      for (var a = arguments.length, c = new Array(a), u = 0; u < a; u++)
        c[u] = arguments[u];
      return s = o.call.apply(o, [this].concat(c)), T(ue(s), "state", {
        keyEntities: []
      }), T(ue(s), "removeKey", function(p) {
        s.setState(function(f) {
          var d = f.keyEntities.map(function(m) {
            return m.key !== p ? m : R(R({}, m), {}, {
              status: bt
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var f = s.state.keyEntities, d = f.filter(function(m) {
            var b = m.status;
            return b !== bt;
          }).length;
          d === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return ye(i, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, u = this.props, p = u.component, f = u.children, d = u.onVisibleChanged;
        u.onAllRemoved;
        var m = vr(u, Ui), b = p || $.Fragment, y = {};
        return Wi.forEach(function(g) {
          y[g] = m[g], delete m[g];
        }), delete m.keys, /* @__PURE__ */ $.createElement(b, m, c.map(function(g, h) {
          var E = g.status, L = vr(g, Xi), S = E === Rt || E === Tt;
          return /* @__PURE__ */ $.createElement(t, he({}, y, {
            key: L.key,
            visible: S,
            eventProps: L,
            onVisibleChanged: function(v) {
              d == null || d(v, {
                key: L.key
              }), v || a.removeKey(L.key);
            }
          }), function(x, v) {
            return f(R(R({}, x), {}, {
              index: h
            }), v);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var u = a.keys, p = c.keyEntities, f = Pt(u), d = Vi(p, f);
        return {
          keyEntities: d.filter(function(m) {
            var b = p.find(function(y) {
              var g = y.key;
              return m.key === g;
            });
            return !(b && b.status === bt && m.status === Lt);
          })
        };
      }
    }]), i;
  }($.Component);
  return T(r, "defaultProps", {
    component: "div"
  }), r;
}
const qi = Gi(Kr);
function Ki(e, t) {
  const {
    children: r,
    upload: n,
    rootClassName: o
  } = e, i = l.useRef(null);
  return l.useImperativeHandle(t, () => i.current), /* @__PURE__ */ l.createElement(Lr, he({}, n, {
    showUploadList: !1,
    rootClassName: o,
    ref: i
  }), r);
}
const rn = /* @__PURE__ */ l.forwardRef(Ki), Zi = (e) => {
  const {
    componentCls: t,
    antCls: r,
    calc: n
  } = e, o = `${t}-list-card`, i = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
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
        padding: n(e.paddingSM).sub(e.lineWidth).equal(),
        paddingInlineStart: n(e.padding).add(e.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: e.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${o}-icon`]: {
          fontSize: n(e.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: n(e.paddingXXS).mul(1.5).equal(),
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
        width: i,
        height: i,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${o}-status-error)`]: {
          border: 0
        },
        // Img
        [`${r}-image`]: {
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
            borderRadius: n(e.borderRadius).sub(e.lineWidth).equal()
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
          marginInlineEnd: n(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, Mt = {
  "&, *": {
    boxSizing: "border-box"
  }
}, Qi = (e) => {
  const {
    componentCls: t,
    calc: r,
    antCls: n
  } = e, o = `${t}-drop-area`, i = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [o]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...Mt,
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
        ...Mt,
        [`${n}-upload-wrapper ${n}-upload${n}-upload-btn`]: {
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
          gap: r(e.paddingXXS).div(2).equal()
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
}, Yi = (e) => {
  const {
    componentCls: t,
    calc: r
  } = e, n = `${t}-list`, o = r(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...Mt,
      // =============================== File List ===============================
      [n]: {
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
          maxHeight: r(o).mul(3).equal(),
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
          [`&${n}-overflow-ping-start ${n}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${n}-overflow-ping-end ${n}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${n}-overflow-ping-end ${n}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${n}-overflow-ping-start ${n}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, Ji = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new te(t).setA(0.85).toRgbString()
  };
}, nn = Ei("Attachments", (e) => {
  const t = At(e, {});
  return [Qi(t), Yi(t), Zi(t)];
}, Ji), es = (e) => e.indexOf("image/") === 0, ke = 200;
function ts(e) {
  return new Promise((t) => {
    if (!e || !e.type || !es(e.type)) {
      t("");
      return;
    }
    const r = new Image();
    if (r.onload = () => {
      const {
        width: n,
        height: o
      } = r, i = n / o, s = i > 1 ? ke : ke * i, a = i > 1 ? ke / i : ke, c = document.createElement("canvas");
      c.width = s, c.height = a, c.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(c), c.getContext("2d").drawImage(r, 0, 0, s, a);
      const p = c.toDataURL();
      document.body.removeChild(c), window.URL.revokeObjectURL(r.src), t(p);
    }, r.crossOrigin = "anonymous", e.type.startsWith("image/svg+xml")) {
      const n = new FileReader();
      n.onload = () => {
        n.result && typeof n.result == "string" && (r.src = n.result);
      }, n.readAsDataURL(e);
    } else if (e.type.startsWith("image/gif")) {
      const n = new FileReader();
      n.onload = () => {
        n.result && t(n.result);
      }, n.readAsDataURL(e);
    } else
      r.src = window.URL.createObjectURL(e);
  });
}
function rs() {
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
function ns(e) {
  const {
    percent: t
  } = e, {
    token: r
  } = He.useToken();
  return /* @__PURE__ */ l.createElement(wn, {
    type: "circle",
    percent: t,
    size: r.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (n) => /* @__PURE__ */ l.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (n || 0).toFixed(0), "%")
  });
}
function os() {
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
const yt = " ", It = "#8c8c8c", on = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], is = [{
  icon: /* @__PURE__ */ l.createElement(Tn, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  icon: /* @__PURE__ */ l.createElement(Ln, null),
  color: It,
  ext: on
}, {
  icon: /* @__PURE__ */ l.createElement(Pn, null),
  color: It,
  ext: ["md", "mdx"]
}, {
  icon: /* @__PURE__ */ l.createElement(Mn, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  icon: /* @__PURE__ */ l.createElement(In, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  icon: /* @__PURE__ */ l.createElement(On, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  icon: /* @__PURE__ */ l.createElement($n, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  icon: /* @__PURE__ */ l.createElement(os, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  icon: /* @__PURE__ */ l.createElement(rs, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function Cr(e, t) {
  return t.some((r) => e.toLowerCase() === `.${r}`);
}
function ss(e) {
  let t = e;
  const r = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let n = 0;
  for (; t >= 1024 && n < r.length - 1; )
    t /= 1024, n++;
  return `${t.toFixed(0)} ${r[n]}`;
}
function as(e, t) {
  const {
    prefixCls: r,
    item: n,
    onRemove: o,
    className: i,
    style: s,
    imageProps: a
  } = e, c = l.useContext(Ce), {
    disabled: u
  } = c || {}, {
    name: p,
    size: f,
    percent: d,
    status: m = "done",
    description: b
  } = n, {
    getPrefixCls: y
  } = Be(), g = y("attachment", r), h = `${g}-list-card`, [E, L, S] = nn(g), [x, v] = l.useMemo(() => {
    const j = p || "", z = j.match(/^(.*)\.[^.]+$/);
    return z ? [z[1], j.slice(z[1].length)] : [j, ""];
  }, [p]), C = l.useMemo(() => Cr(v, on), [v]), _ = l.useMemo(() => b || (m === "uploading" ? `${d || 0}%` : m === "error" ? n.response || yt : f ? ss(f) : yt), [m, d]), [O, w] = l.useMemo(() => {
    for (const {
      ext: j,
      icon: z,
      color: q
    } of is)
      if (Cr(v, j))
        return [z, q];
    return [/* @__PURE__ */ l.createElement(_n, {
      key: "defaultIcon"
    }), It];
  }, [v]), [M, P] = l.useState();
  l.useEffect(() => {
    if (n.originFileObj) {
      let j = !0;
      return ts(n.originFileObj).then((z) => {
        j && P(z);
      }), () => {
        j = !1;
      };
    }
    P(void 0);
  }, [n.originFileObj]);
  let I = null;
  const F = n.thumbUrl || n.url || M, k = C && (n.originFileObj || F);
  return k ? I = /* @__PURE__ */ l.createElement(l.Fragment, null, F && /* @__PURE__ */ l.createElement(En, he({
    alt: "preview",
    src: F
  }, a)), m !== "done" && /* @__PURE__ */ l.createElement("div", {
    className: `${h}-img-mask`
  }, m === "uploading" && d !== void 0 && /* @__PURE__ */ l.createElement(ns, {
    percent: d,
    prefixCls: h
  }), m === "error" && /* @__PURE__ */ l.createElement("div", {
    className: `${h}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${h}-ellipsis-prefix`
  }, _)))) : I = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement("div", {
    className: `${h}-icon`,
    style: {
      color: w
    }
  }, O), /* @__PURE__ */ l.createElement("div", {
    className: `${h}-content`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${h}-name`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${h}-ellipsis-prefix`
  }, x ?? yt), /* @__PURE__ */ l.createElement("div", {
    className: `${h}-ellipsis-suffix`
  }, v)), /* @__PURE__ */ l.createElement("div", {
    className: `${h}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${h}-ellipsis-prefix`
  }, _)))), E(/* @__PURE__ */ l.createElement("div", {
    className: Q(h, {
      [`${h}-status-${m}`]: m,
      [`${h}-type-preview`]: k,
      [`${h}-type-overview`]: !k
    }, i, L, S),
    style: s,
    ref: t
  }, I, !u && o && /* @__PURE__ */ l.createElement("button", {
    type: "button",
    className: `${h}-remove`,
    onClick: () => {
      o(n);
    }
  }, /* @__PURE__ */ l.createElement(Rn, null))));
}
const sn = /* @__PURE__ */ l.forwardRef(as), _r = 1;
function ls(e) {
  const {
    prefixCls: t,
    items: r,
    onRemove: n,
    overflow: o,
    upload: i,
    listClassName: s,
    listStyle: a,
    itemClassName: c,
    uploadClassName: u,
    uploadStyle: p,
    itemStyle: f,
    imageProps: d
  } = e, m = `${t}-list`, b = l.useRef(null), [y, g] = l.useState(!1), {
    disabled: h
  } = l.useContext(Ce);
  l.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [E, L] = l.useState(!1), [S, x] = l.useState(!1), v = () => {
    const w = b.current;
    w && (o === "scrollX" ? (L(Math.abs(w.scrollLeft) >= _r), x(w.scrollWidth - w.clientWidth - Math.abs(w.scrollLeft) >= _r)) : o === "scrollY" && (L(w.scrollTop !== 0), x(w.scrollHeight - w.clientHeight !== w.scrollTop)));
  };
  l.useEffect(() => {
    v();
  }, [o, r.length]);
  const C = (w) => {
    const M = b.current;
    M && M.scrollTo({
      left: M.scrollLeft + w * M.clientWidth,
      behavior: "smooth"
    });
  }, _ = () => {
    C(-1);
  }, O = () => {
    C(1);
  };
  return /* @__PURE__ */ l.createElement("div", {
    className: Q(m, {
      [`${m}-overflow-${e.overflow}`]: o,
      [`${m}-overflow-ping-start`]: E,
      [`${m}-overflow-ping-end`]: S
    }, s),
    ref: b,
    onScroll: v,
    style: a
  }, /* @__PURE__ */ l.createElement(qi, {
    keys: r.map((w) => ({
      key: w.uid,
      item: w
    })),
    motionName: `${m}-card-motion`,
    component: !1,
    motionAppear: y,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: w,
    item: M,
    className: P,
    style: I
  }) => /* @__PURE__ */ l.createElement(sn, {
    key: w,
    prefixCls: t,
    item: M,
    onRemove: n,
    className: Q(P, c),
    imageProps: d,
    style: {
      ...I,
      ...f
    }
  })), !h && /* @__PURE__ */ l.createElement(rn, {
    upload: i
  }, /* @__PURE__ */ l.createElement(at, {
    className: Q(u, `${m}-upload-btn`),
    style: p,
    type: "dashed"
  }, /* @__PURE__ */ l.createElement(An, {
    className: `${m}-upload-btn-icon`
  }))), o === "scrollX" && /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(at, {
    size: "small",
    shape: "circle",
    className: `${m}-prev-btn`,
    icon: /* @__PURE__ */ l.createElement(Fn, null),
    onClick: _
  }), /* @__PURE__ */ l.createElement(at, {
    size: "small",
    shape: "circle",
    className: `${m}-next-btn`,
    icon: /* @__PURE__ */ l.createElement(kn, null),
    onClick: O
  })));
}
function cs(e, t) {
  const {
    prefixCls: r,
    placeholder: n = {},
    upload: o,
    className: i,
    style: s
  } = e, a = `${r}-placeholder`, c = n || {}, {
    disabled: u
  } = l.useContext(Ce), [p, f] = l.useState(!1), d = () => {
    f(!0);
  }, m = (g) => {
    g.currentTarget.contains(g.relatedTarget) || f(!1);
  }, b = () => {
    f(!1);
  }, y = /* @__PURE__ */ l.isValidElement(n) ? n : /* @__PURE__ */ l.createElement(Cn, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ l.createElement(lt.Text, {
    className: `${a}-icon`
  }, c.icon), /* @__PURE__ */ l.createElement(lt.Title, {
    className: `${a}-title`,
    level: 5
  }, c.title), /* @__PURE__ */ l.createElement(lt.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, c.description));
  return /* @__PURE__ */ l.createElement("div", {
    className: Q(a, {
      [`${a}-drag-in`]: p,
      [`${a}-disabled`]: u
    }, i),
    onDragEnter: d,
    onDragLeave: m,
    onDrop: b,
    "aria-hidden": u,
    style: s
  }, /* @__PURE__ */ l.createElement(Lr.Dragger, he({
    showUploadList: !1
  }, o, {
    ref: t,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), y));
}
const us = /* @__PURE__ */ l.forwardRef(cs);
function fs(e, t) {
  const {
    prefixCls: r,
    rootClassName: n,
    rootStyle: o,
    className: i,
    style: s,
    items: a,
    children: c,
    getDropContainer: u,
    placeholder: p,
    onChange: f,
    onRemove: d,
    overflow: m,
    imageProps: b,
    disabled: y,
    classNames: g = {},
    styles: h = {},
    ...E
  } = e, {
    getPrefixCls: L,
    direction: S
  } = Be(), x = L("attachment", r), v = Do("attachments"), {
    classNames: C,
    styles: _
  } = v, O = l.useRef(null), w = l.useRef(null);
  l.useImperativeHandle(t, () => ({
    nativeElement: O.current,
    upload: (D) => {
      var N, K;
      const G = (K = (N = w.current) == null ? void 0 : N.nativeElement) == null ? void 0 : K.querySelector('input[type="file"]');
      if (G) {
        const ae = new DataTransfer();
        ae.items.add(D), G.files = ae.files, G.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [M, P, I] = nn(x), F = Q(P, I), [k, j] = Ko([], {
    value: a
  }), z = ve((D) => {
    j(D.fileList), f == null || f(D);
  }), q = {
    ...E,
    fileList: k,
    onChange: z
  }, fe = (D) => Promise.resolve(typeof d == "function" ? d(D) : d).then((G) => {
    if (G === !1)
      return;
    const N = k.filter((K) => K.uid !== D.uid);
    z({
      file: {
        ...D,
        status: "removed"
      },
      fileList: N
    });
  });
  let oe;
  const V = (D, G, N) => {
    const K = typeof p == "function" ? p(D) : p;
    return /* @__PURE__ */ l.createElement(us, {
      placeholder: K,
      upload: q,
      prefixCls: x,
      className: Q(C.placeholder, g.placeholder),
      style: {
        ..._.placeholder,
        ...h.placeholder,
        ...G == null ? void 0 : G.style
      },
      ref: N
    });
  };
  if (c)
    oe = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(rn, {
      upload: q,
      rootClassName: n,
      ref: w
    }, c), /* @__PURE__ */ l.createElement(gr, {
      getDropContainer: u,
      prefixCls: x,
      className: Q(F, n)
    }, V("drop")));
  else {
    const D = k.length > 0;
    oe = /* @__PURE__ */ l.createElement("div", {
      className: Q(x, F, {
        [`${x}-rtl`]: S === "rtl"
      }, i, n),
      style: {
        ...o,
        ...s
      },
      dir: S || "ltr",
      ref: O
    }, /* @__PURE__ */ l.createElement(ls, {
      prefixCls: x,
      items: k,
      onRemove: fe,
      overflow: m,
      upload: q,
      listClassName: Q(C.list, g.list),
      listStyle: {
        ..._.list,
        ...h.list,
        ...!D && {
          display: "none"
        }
      },
      uploadClassName: Q(C.upload, g.upload),
      uploadStyle: {
        ..._.upload,
        ...h.upload
      },
      itemClassName: Q(C.item, g.item),
      itemStyle: {
        ..._.item,
        ...h.item
      },
      imageProps: b
    }), V("inline", D ? {
      style: {
        display: "none"
      }
    } : {}, w), /* @__PURE__ */ l.createElement(gr, {
      getDropContainer: u || (() => O.current),
      prefixCls: x,
      className: F
    }, V("drop")));
  }
  return M(/* @__PURE__ */ l.createElement(Ce.Provider, {
    value: {
      disabled: y
    }
  }, oe));
}
const an = /* @__PURE__ */ l.forwardRef(fs);
an.FileCard = sn;
new Intl.Collator(0, {
  numeric: 1
}).compare;
typeof process < "u" && process.versions && process.versions.node;
var ne;
class Ss extends TransformStream {
  /** Constructs a new instance. */
  constructor(r = {
    allowCR: !1
  }) {
    super({
      transform: (n, o) => {
        for (n = de(this, ne) + n; ; ) {
          const i = n.indexOf(`
`), s = r.allowCR ? n.indexOf("\r") : -1;
          if (s !== -1 && s !== n.length - 1 && (i === -1 || i - 1 > s)) {
            o.enqueue(n.slice(0, s)), n = n.slice(s + 1);
            continue;
          }
          if (i === -1) break;
          const a = n[i - 1] === "\r" ? i - 1 : i;
          o.enqueue(n.slice(0, a)), n = n.slice(i + 1);
        }
        Bt(this, ne, n);
      },
      flush: (n) => {
        if (de(this, ne) === "") return;
        const o = r.allowCR && de(this, ne).endsWith("\r") ? de(this, ne).slice(0, -1) : de(this, ne);
        n.enqueue(o);
      }
    });
    Ht(this, ne, "");
  }
}
ne = new WeakMap();
function ds(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function ps() {
  const e = document.querySelector(".gradio-container");
  if (!e)
    return "";
  const t = e.className.match(/gradio-container-(.+)/);
  return t ? t[1] : "";
}
const ms = +ps()[0];
function Rr(e, t, r) {
  const n = ms >= 5 ? "gradio_api/" : "";
  return e == null ? r ? `/proxy=${r}${n}file=` : `${t}${n}file=` : ds(e) ? e : r ? `/proxy=${r}${n}file=${e}` : `${t}/${n}file=${e}`;
}
const gs = ({
  item: e,
  urlRoot: t,
  urlProxyUrl: r,
  ...n
}) => {
  const o = Tr(() => e ? typeof e == "string" ? {
    url: e.startsWith("http") ? e : Rr(e, t, r),
    uid: e,
    name: e.split("/").pop()
  } : {
    ...e,
    uid: e.uid || e.path || e.url,
    name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
    url: e.url || Rr(e.path, t, r)
  } : {}, [e, r, t]);
  return /* @__PURE__ */ X.jsx(an.FileCard, {
    ...n,
    imageProps: {
      ...n.imageProps
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
};
function hs(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const xs = Co(({
  setSlotParams: e,
  imageProps: t,
  slots: r,
  children: n,
  ...o
}) => {
  const i = hs(t == null ? void 0 : t.preview), s = r["imageProps.preview.mask"] || r["imageProps.preview.closeIcon"] || r["imageProps.preview.toolbarRender"] || r["imageProps.preview.imageRender"] || (t == null ? void 0 : t.preview) !== !1, a = dt(i.getContainer), c = dt(i.toolbarRender), u = dt(i.imageRender);
  return /* @__PURE__ */ X.jsxs(X.Fragment, {
    children: [/* @__PURE__ */ X.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ X.jsx(gs, {
      ...o,
      imageProps: {
        ...t,
        preview: s ? Io({
          ...i,
          getContainer: a,
          toolbarRender: r["imageProps.preview.toolbarRender"] ? nr({
            slots: r,
            key: "imageProps.preview.toolbarRender"
          }) : c,
          imageRender: r["imageProps.preview.imageRender"] ? nr({
            slots: r,
            key: "imageProps.preview.imageRender"
          }) : u,
          ...r["imageProps.preview.mask"] || Reflect.has(i, "mask") ? {
            mask: r["imageProps.preview.mask"] ? /* @__PURE__ */ X.jsx(we, {
              slot: r["imageProps.preview.mask"]
            }) : i.mask
          } : {},
          closeIcon: r["imageProps.preview.closeIcon"] ? /* @__PURE__ */ X.jsx(we, {
            slot: r["imageProps.preview.closeIcon"]
          }) : i.closeIcon
        }) : !1,
        placeholder: r["imageProps.placeholder"] ? /* @__PURE__ */ X.jsx(we, {
          slot: r["imageProps.placeholder"]
        }) : t == null ? void 0 : t.placeholder
      }
    })]
  });
});
export {
  xs as AttachmentsFileCard,
  xs as default
};
