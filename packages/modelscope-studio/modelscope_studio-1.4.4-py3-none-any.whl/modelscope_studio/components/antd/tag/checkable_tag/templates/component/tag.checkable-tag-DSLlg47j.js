import { Z as m, g as Y, t as Z, s as _ } from "./Index-IDl92nn9.js";
const P = window.ms_globals.React, j = window.ms_globals.React.useMemo, G = window.ms_globals.React.useState, J = window.ms_globals.React.useEffect, S = window.ms_globals.ReactDOM.createPortal, H = window.ms_globals.antd.Tag;
var A = {
  exports: {}
}, w = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Q = P, X = Symbol.for("react.element"), $ = Symbol.for("react.fragment"), ee = Object.prototype.hasOwnProperty, te = Q.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, se = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function D(o, t, l) {
  var n, r = {}, e = null, s = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) ee.call(t, n) && !se.hasOwnProperty(n) && (r[n] = t[n]);
  if (o && o.defaultProps) for (n in t = o.defaultProps, t) r[n] === void 0 && (r[n] = t[n]);
  return {
    $$typeof: X,
    type: o,
    key: e,
    ref: s,
    props: r,
    _owner: te.current
  };
}
w.Fragment = $;
w.jsx = D;
w.jsxs = D;
A.exports = w;
var oe = A.exports;
const {
  SvelteComponent: ne,
  assign: h,
  binding_callbacks: x,
  check_outros: re,
  children: L,
  claim_element: N,
  claim_space: le,
  component_subscribe: k,
  compute_slots: ae,
  create_slot: ue,
  detach: i,
  element: q,
  empty: R,
  exclude_internal_props: E,
  get_all_dirty_from_scope: ce,
  get_slot_changes: ie,
  group_outros: _e,
  init: fe,
  insert_hydration: g,
  safe_not_equal: de,
  set_custom_element_data: K,
  space: pe,
  transition_in: b,
  transition_out: v,
  update_slot_base: me
} = window.__gradio__svelte__internal, {
  beforeUpdate: ge,
  getContext: be,
  onDestroy: we,
  setContext: Ie
} = window.__gradio__svelte__internal;
function T(o) {
  let t, l;
  const n = (
    /*#slots*/
    o[7].default
  ), r = ue(
    n,
    o,
    /*$$scope*/
    o[6],
    null
  );
  return {
    c() {
      t = q("svelte-slot"), r && r.c(), this.h();
    },
    l(e) {
      t = N(e, "SVELTE-SLOT", {
        class: !0
      });
      var s = L(t);
      r && r.l(s), s.forEach(i), this.h();
    },
    h() {
      K(t, "class", "svelte-1rt0kpf");
    },
    m(e, s) {
      g(e, t, s), r && r.m(t, null), o[9](t), l = !0;
    },
    p(e, s) {
      r && r.p && (!l || s & /*$$scope*/
      64) && me(
        r,
        n,
        e,
        /*$$scope*/
        e[6],
        l ? ie(
          n,
          /*$$scope*/
          e[6],
          s,
          null
        ) : ce(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      l || (b(r, e), l = !0);
    },
    o(e) {
      v(r, e), l = !1;
    },
    d(e) {
      e && i(t), r && r.d(e), o[9](null);
    }
  };
}
function ve(o) {
  let t, l, n, r, e = (
    /*$$slots*/
    o[4].default && T(o)
  );
  return {
    c() {
      t = q("react-portal-target"), l = pe(), e && e.c(), n = R(), this.h();
    },
    l(s) {
      t = N(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), L(t).forEach(i), l = le(s), e && e.l(s), n = R(), this.h();
    },
    h() {
      K(t, "class", "svelte-1rt0kpf");
    },
    m(s, u) {
      g(s, t, u), o[8](t), g(s, l, u), e && e.m(s, u), g(s, n, u), r = !0;
    },
    p(s, [u]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, u), u & /*$$slots*/
      16 && b(e, 1)) : (e = T(s), e.c(), b(e, 1), e.m(n.parentNode, n)) : e && (_e(), v(e, 1, 1, () => {
        e = null;
      }), re());
    },
    i(s) {
      r || (b(e), r = !0);
    },
    o(s) {
      v(e), r = !1;
    },
    d(s) {
      s && (i(t), i(l), i(n)), o[8](null), e && e.d(s);
    }
  };
}
function C(o) {
  const {
    svelteInit: t,
    ...l
  } = o;
  return l;
}
function ye(o, t, l) {
  let n, r, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const u = ae(e);
  let {
    svelteInit: c
  } = t;
  const f = m(C(t)), d = m();
  k(o, d, (a) => l(0, n = a));
  const p = m();
  k(o, p, (a) => l(1, r = a));
  const y = [], M = be("$$ms-gr-react-wrapper"), {
    slotKey: U,
    slotIndex: B,
    subSlotIndex: F
  } = Y() || {}, V = c({
    parent: M,
    props: f,
    target: d,
    slot: p,
    slotKey: U,
    slotIndex: B,
    subSlotIndex: F,
    onDestroy(a) {
      y.push(a);
    }
  });
  Ie("$$ms-gr-react-wrapper", V), ge(() => {
    f.set(C(t));
  }), we(() => {
    y.forEach((a) => a());
  });
  function W(a) {
    x[a ? "unshift" : "push"](() => {
      n = a, d.set(n);
    });
  }
  function z(a) {
    x[a ? "unshift" : "push"](() => {
      r = a, p.set(r);
    });
  }
  return o.$$set = (a) => {
    l(17, t = h(h({}, t), E(a))), "svelteInit" in a && l(5, c = a.svelteInit), "$$scope" in a && l(6, s = a.$$scope);
  }, t = E(t), [n, r, d, p, u, c, s, e, W, z];
}
class Se extends ne {
  constructor(t) {
    super(), fe(this, t, ye, ve, de, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Te
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, I = window.ms_globals.tree;
function he(o, t = {}) {
  function l(n) {
    const r = m(), e = new Se({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const u = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: o,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? I;
          return c.nodes = [...c.nodes, u], O({
            createPortal: S,
            node: I
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((f) => f.svelteInstance !== r), O({
              createPortal: S,
              node: I
            });
          }), u;
        },
        ...n.props
      }
    });
    return r.set(e), e;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise.then(() => {
      n(l);
    });
  });
}
function xe(o) {
  const [t, l] = G(() => _(o));
  return J(() => {
    let n = !0;
    return o.subscribe((e) => {
      n && (n = !1, e === t) || l(e);
    });
  }, [o]), t;
}
function ke(o) {
  const t = j(() => Z(o, (l) => l), [o]);
  return xe(t);
}
function Re(o, t) {
  const l = j(() => P.Children.toArray(o.originalChildren || o).filter((e) => e.props.node && !e.props.node.ignore && (!e.props.nodeSlotKey || t)).sort((e, s) => {
    if (e.props.node.slotIndex && s.props.node.slotIndex) {
      const u = _(e.props.node.slotIndex) || 0, c = _(s.props.node.slotIndex) || 0;
      return u - c === 0 && e.props.node.subSlotIndex && s.props.node.subSlotIndex ? (_(e.props.node.subSlotIndex) || 0) - (_(s.props.node.subSlotIndex) || 0) : u - c;
    }
    return 0;
  }).map((e) => e.props.node.target), [o, t]);
  return ke(l);
}
const Ce = he(({
  onChange: o,
  onValueChange: t,
  children: l,
  label: n,
  ...r
}) => {
  const e = Re(l);
  return /* @__PURE__ */ oe.jsx(H.CheckableTag, {
    ...r,
    onChange: (s) => {
      o == null || o(s), t(s);
    },
    children: e.length > 0 ? l : n
  });
});
export {
  Ce as CheckableTag,
  Ce as default
};
