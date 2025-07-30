var pt = Object.defineProperty;
var Ie = (s) => {
  throw TypeError(s);
};
var ht = (s, t, e) => t in s ? pt(s, t, { enumerable: !0, configurable: !0, writable: !0, value: e }) : s[t] = e;
var S = (s, t, e) => ht(s, typeof t != "symbol" ? t + "" : t, e), mt = (s, t, e) => t.has(s) || Ie("Cannot " + e);
var Re = (s, t, e) => t.has(s) ? Ie("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(s) : t.set(s, e);
var de = (s, t, e) => (mt(s, t, "access private method"), e);
const {
  SvelteComponent: gt,
  append_hydration: be,
  assign: ft,
  attr: z,
  binding_callbacks: $t,
  children: ee,
  claim_element: Ye,
  claim_space: We,
  claim_svg_element: Fe,
  create_slot: Dt,
  detach: N,
  element: Qe,
  empty: ze,
  get_all_dirty_from_scope: vt,
  get_slot_changes: Ft,
  get_spread_update: yt,
  init: bt,
  insert_hydration: ie,
  listen: wt,
  noop: Ct,
  safe_not_equal: kt,
  set_dynamic_element_data: Le,
  set_style: k,
  space: Ke,
  svg_element: ye,
  toggle_class: R,
  transition_in: Ve,
  transition_out: Je,
  update_slot_base: Et
} = window.__gradio__svelte__internal;
function Oe(s) {
  let t, e, n, a, o;
  return {
    c() {
      t = ye("svg"), e = ye("line"), n = ye("line"), this.h();
    },
    l(i) {
      t = Fe(i, "svg", { class: !0, xmlns: !0, viewBox: !0 });
      var r = ee(t);
      e = Fe(r, "line", {
        x1: !0,
        y1: !0,
        x2: !0,
        y2: !0,
        stroke: !0,
        "stroke-width": !0
      }), ee(e).forEach(N), n = Fe(r, "line", {
        x1: !0,
        y1: !0,
        x2: !0,
        y2: !0,
        stroke: !0,
        "stroke-width": !0
      }), ee(n).forEach(N), r.forEach(N), this.h();
    },
    h() {
      z(e, "x1", "1"), z(e, "y1", "9"), z(e, "x2", "9"), z(e, "y2", "1"), z(e, "stroke", "gray"), z(e, "stroke-width", "0.5"), z(n, "x1", "5"), z(n, "y1", "9"), z(n, "x2", "9"), z(n, "y2", "5"), z(n, "stroke", "gray"), z(n, "stroke-width", "0.5"), z(t, "class", "resize-handle svelte-239wnu"), z(t, "xmlns", "http://www.w3.org/2000/svg"), z(t, "viewBox", "0 0 10 10");
    },
    m(i, r) {
      ie(i, t, r), be(t, e), be(t, n), a || (o = wt(
        t,
        "mousedown",
        /*resize*/
        s[27]
      ), a = !0);
    },
    p: Ct,
    d(i) {
      i && N(t), a = !1, o();
    }
  };
}
function At(s) {
  var F;
  let t, e, n, a, o;
  const i = (
    /*#slots*/
    s[31].default
  ), r = Dt(
    i,
    s,
    /*$$scope*/
    s[30],
    null
  );
  let l = (
    /*resizable*/
    s[19] && Oe(s)
  ), m = [
    { "data-testid": (
      /*test_id*/
      s[11]
    ) },
    { id: (
      /*elem_id*/
      s[6]
    ) },
    {
      class: n = "block " + /*elem_classes*/
      (((F = s[7]) == null ? void 0 : F.join(" ")) || "") + " svelte-239wnu"
    },
    {
      dir: a = /*rtl*/
      s[20] ? "rtl" : "ltr"
    }
  ], g = {};
  for (let u = 0; u < m.length; u += 1)
    g = ft(g, m[u]);
  return {
    c() {
      t = Qe(
        /*tag*/
        s[25]
      ), r && r.c(), e = Ke(), l && l.c(), this.h();
    },
    l(u) {
      t = Ye(
        u,
        /*tag*/
        (s[25] || "null").toUpperCase(),
        {
          "data-testid": !0,
          id: !0,
          class: !0,
          dir: !0
        }
      );
      var $ = ee(t);
      r && r.l($), e = We($), l && l.l($), $.forEach(N), this.h();
    },
    h() {
      Le(
        /*tag*/
        s[25]
      )(t, g), R(
        t,
        "hidden",
        /*visible*/
        s[14] === !1
      ), R(
        t,
        "padded",
        /*padding*/
        s[10]
      ), R(
        t,
        "flex",
        /*flex*/
        s[1]
      ), R(
        t,
        "border_focus",
        /*border_mode*/
        s[9] === "focus"
      ), R(
        t,
        "border_contrast",
        /*border_mode*/
        s[9] === "contrast"
      ), R(t, "hide-container", !/*explicit_call*/
      s[12] && !/*container*/
      s[13]), R(
        t,
        "fullscreen",
        /*fullscreen*/
        s[0]
      ), R(
        t,
        "animating",
        /*fullscreen*/
        s[0] && /*preexpansionBoundingRect*/
        s[24] !== null
      ), R(
        t,
        "auto-margin",
        /*scale*/
        s[17] === null
      ), k(
        t,
        "height",
        /*fullscreen*/
        s[0] ? void 0 : (
          /*get_dimension*/
          s[26](
            /*height*/
            s[2]
          )
        )
      ), k(
        t,
        "min-height",
        /*fullscreen*/
        s[0] ? void 0 : (
          /*get_dimension*/
          s[26](
            /*min_height*/
            s[3]
          )
        )
      ), k(
        t,
        "max-height",
        /*fullscreen*/
        s[0] ? void 0 : (
          /*get_dimension*/
          s[26](
            /*max_height*/
            s[4]
          )
        )
      ), k(
        t,
        "--start-top",
        /*preexpansionBoundingRect*/
        s[24] ? `${/*preexpansionBoundingRect*/
        s[24].top}px` : "0px"
      ), k(
        t,
        "--start-left",
        /*preexpansionBoundingRect*/
        s[24] ? `${/*preexpansionBoundingRect*/
        s[24].left}px` : "0px"
      ), k(
        t,
        "--start-width",
        /*preexpansionBoundingRect*/
        s[24] ? `${/*preexpansionBoundingRect*/
        s[24].width}px` : "0px"
      ), k(
        t,
        "--start-height",
        /*preexpansionBoundingRect*/
        s[24] ? `${/*preexpansionBoundingRect*/
        s[24].height}px` : "0px"
      ), k(
        t,
        "width",
        /*fullscreen*/
        s[0] ? void 0 : typeof /*width*/
        s[5] == "number" ? `calc(min(${/*width*/
        s[5]}px, 100%))` : (
          /*get_dimension*/
          s[26](
            /*width*/
            s[5]
          )
        )
      ), k(
        t,
        "border-style",
        /*variant*/
        s[8]
      ), k(
        t,
        "overflow",
        /*allow_overflow*/
        s[15] ? (
          /*overflow_behavior*/
          s[16]
        ) : "hidden"
      ), k(
        t,
        "flex-grow",
        /*scale*/
        s[17]
      ), k(t, "min-width", `calc(min(${/*min_width*/
      s[18]}px, 100%))`), k(t, "border-width", "var(--block-border-width)");
    },
    m(u, $) {
      ie(u, t, $), r && r.m(t, null), be(t, e), l && l.m(t, null), s[32](t), o = !0;
    },
    p(u, $) {
      var B;
      r && r.p && (!o || $[0] & /*$$scope*/
      1073741824) && Et(
        r,
        i,
        u,
        /*$$scope*/
        u[30],
        o ? Ft(
          i,
          /*$$scope*/
          u[30],
          $,
          null
        ) : vt(
          /*$$scope*/
          u[30]
        ),
        null
      ), /*resizable*/
      u[19] ? l ? l.p(u, $) : (l = Oe(u), l.c(), l.m(t, null)) : l && (l.d(1), l = null), Le(
        /*tag*/
        u[25]
      )(t, g = yt(m, [
        (!o || $[0] & /*test_id*/
        2048) && { "data-testid": (
          /*test_id*/
          u[11]
        ) },
        (!o || $[0] & /*elem_id*/
        64) && { id: (
          /*elem_id*/
          u[6]
        ) },
        (!o || $[0] & /*elem_classes*/
        128 && n !== (n = "block " + /*elem_classes*/
        (((B = u[7]) == null ? void 0 : B.join(" ")) || "") + " svelte-239wnu")) && { class: n },
        (!o || $[0] & /*rtl*/
        1048576 && a !== (a = /*rtl*/
        u[20] ? "rtl" : "ltr")) && { dir: a }
      ])), R(
        t,
        "hidden",
        /*visible*/
        u[14] === !1
      ), R(
        t,
        "padded",
        /*padding*/
        u[10]
      ), R(
        t,
        "flex",
        /*flex*/
        u[1]
      ), R(
        t,
        "border_focus",
        /*border_mode*/
        u[9] === "focus"
      ), R(
        t,
        "border_contrast",
        /*border_mode*/
        u[9] === "contrast"
      ), R(t, "hide-container", !/*explicit_call*/
      u[12] && !/*container*/
      u[13]), R(
        t,
        "fullscreen",
        /*fullscreen*/
        u[0]
      ), R(
        t,
        "animating",
        /*fullscreen*/
        u[0] && /*preexpansionBoundingRect*/
        u[24] !== null
      ), R(
        t,
        "auto-margin",
        /*scale*/
        u[17] === null
      ), $[0] & /*fullscreen, height*/
      5 && k(
        t,
        "height",
        /*fullscreen*/
        u[0] ? void 0 : (
          /*get_dimension*/
          u[26](
            /*height*/
            u[2]
          )
        )
      ), $[0] & /*fullscreen, min_height*/
      9 && k(
        t,
        "min-height",
        /*fullscreen*/
        u[0] ? void 0 : (
          /*get_dimension*/
          u[26](
            /*min_height*/
            u[3]
          )
        )
      ), $[0] & /*fullscreen, max_height*/
      17 && k(
        t,
        "max-height",
        /*fullscreen*/
        u[0] ? void 0 : (
          /*get_dimension*/
          u[26](
            /*max_height*/
            u[4]
          )
        )
      ), $[0] & /*preexpansionBoundingRect*/
      16777216 && k(
        t,
        "--start-top",
        /*preexpansionBoundingRect*/
        u[24] ? `${/*preexpansionBoundingRect*/
        u[24].top}px` : "0px"
      ), $[0] & /*preexpansionBoundingRect*/
      16777216 && k(
        t,
        "--start-left",
        /*preexpansionBoundingRect*/
        u[24] ? `${/*preexpansionBoundingRect*/
        u[24].left}px` : "0px"
      ), $[0] & /*preexpansionBoundingRect*/
      16777216 && k(
        t,
        "--start-width",
        /*preexpansionBoundingRect*/
        u[24] ? `${/*preexpansionBoundingRect*/
        u[24].width}px` : "0px"
      ), $[0] & /*preexpansionBoundingRect*/
      16777216 && k(
        t,
        "--start-height",
        /*preexpansionBoundingRect*/
        u[24] ? `${/*preexpansionBoundingRect*/
        u[24].height}px` : "0px"
      ), $[0] & /*fullscreen, width*/
      33 && k(
        t,
        "width",
        /*fullscreen*/
        u[0] ? void 0 : typeof /*width*/
        u[5] == "number" ? `calc(min(${/*width*/
        u[5]}px, 100%))` : (
          /*get_dimension*/
          u[26](
            /*width*/
            u[5]
          )
        )
      ), $[0] & /*variant*/
      256 && k(
        t,
        "border-style",
        /*variant*/
        u[8]
      ), $[0] & /*allow_overflow, overflow_behavior*/
      98304 && k(
        t,
        "overflow",
        /*allow_overflow*/
        u[15] ? (
          /*overflow_behavior*/
          u[16]
        ) : "hidden"
      ), $[0] & /*scale*/
      131072 && k(
        t,
        "flex-grow",
        /*scale*/
        u[17]
      ), $[0] & /*min_width*/
      262144 && k(t, "min-width", `calc(min(${/*min_width*/
      u[18]}px, 100%))`);
    },
    i(u) {
      o || (Ve(r, u), o = !0);
    },
    o(u) {
      Je(r, u), o = !1;
    },
    d(u) {
      u && N(t), r && r.d(u), l && l.d(), s[32](null);
    }
  };
}
function Pe(s) {
  let t;
  return {
    c() {
      t = Qe("div"), this.h();
    },
    l(e) {
      t = Ye(e, "DIV", { class: !0 }), ee(t).forEach(N), this.h();
    },
    h() {
      z(t, "class", "placeholder svelte-239wnu"), k(
        t,
        "height",
        /*placeholder_height*/
        s[22] + "px"
      ), k(
        t,
        "width",
        /*placeholder_width*/
        s[23] + "px"
      );
    },
    m(e, n) {
      ie(e, t, n);
    },
    p(e, n) {
      n[0] & /*placeholder_height*/
      4194304 && k(
        t,
        "height",
        /*placeholder_height*/
        e[22] + "px"
      ), n[0] & /*placeholder_width*/
      8388608 && k(
        t,
        "width",
        /*placeholder_width*/
        e[23] + "px"
      );
    },
    d(e) {
      e && N(t);
    }
  };
}
function xt(s) {
  let t, e, n, a = (
    /*tag*/
    s[25] && At(s)
  ), o = (
    /*fullscreen*/
    s[0] && Pe(s)
  );
  return {
    c() {
      a && a.c(), t = Ke(), o && o.c(), e = ze();
    },
    l(i) {
      a && a.l(i), t = We(i), o && o.l(i), e = ze();
    },
    m(i, r) {
      a && a.m(i, r), ie(i, t, r), o && o.m(i, r), ie(i, e, r), n = !0;
    },
    p(i, r) {
      /*tag*/
      i[25] && a.p(i, r), /*fullscreen*/
      i[0] ? o ? o.p(i, r) : (o = Pe(i), o.c(), o.m(e.parentNode, e)) : o && (o.d(1), o = null);
    },
    i(i) {
      n || (Ve(a, i), n = !0);
    },
    o(i) {
      Je(a, i), n = !1;
    },
    d(i) {
      i && (N(t), N(e)), a && a.d(i), o && o.d(i);
    }
  };
}
function St(s, t, e) {
  let { $$slots: n = {}, $$scope: a } = t, { height: o = void 0 } = t, { min_height: i = void 0 } = t, { max_height: r = void 0 } = t, { width: l = void 0 } = t, { elem_id: m = "" } = t, { elem_classes: g = [] } = t, { variant: F = "solid" } = t, { border_mode: u = "base" } = t, { padding: $ = !0 } = t, { type: B = "normal" } = t, { test_id: w = void 0 } = t, { explicit_call: y = !1 } = t, { container: x = !0 } = t, { visible: d = !0 } = t, { allow_overflow: c = !0 } = t, { overflow_behavior: _ = "auto" } = t, { scale: p = null } = t, { min_width: h = 0 } = t, { flex: D = !1 } = t, { resizable: b = !1 } = t, { rtl: v = !1 } = t, { fullscreen: C = !1 } = t, q = C, T, re = B === "fieldset" ? "fieldset" : "div", Q = 0, se = 0, K = null;
  function V(f) {
    C && f.key === "Escape" && e(0, C = !1);
  }
  const I = (f) => {
    if (f !== void 0) {
      if (typeof f == "number")
        return f + "px";
      if (typeof f == "string")
        return f;
    }
  }, P = (f) => {
    let L = f.clientY;
    const le = (U) => {
      const W = U.clientY - L;
      L = U.clientY, e(21, T.style.height = `${T.offsetHeight + W}px`, T);
    }, M = () => {
      window.removeEventListener("mousemove", le), window.removeEventListener("mouseup", M);
    };
    window.addEventListener("mousemove", le), window.addEventListener("mouseup", M);
  };
  function G(f) {
    $t[f ? "unshift" : "push"](() => {
      T = f, e(21, T);
    });
  }
  return s.$$set = (f) => {
    "height" in f && e(2, o = f.height), "min_height" in f && e(3, i = f.min_height), "max_height" in f && e(4, r = f.max_height), "width" in f && e(5, l = f.width), "elem_id" in f && e(6, m = f.elem_id), "elem_classes" in f && e(7, g = f.elem_classes), "variant" in f && e(8, F = f.variant), "border_mode" in f && e(9, u = f.border_mode), "padding" in f && e(10, $ = f.padding), "type" in f && e(28, B = f.type), "test_id" in f && e(11, w = f.test_id), "explicit_call" in f && e(12, y = f.explicit_call), "container" in f && e(13, x = f.container), "visible" in f && e(14, d = f.visible), "allow_overflow" in f && e(15, c = f.allow_overflow), "overflow_behavior" in f && e(16, _ = f.overflow_behavior), "scale" in f && e(17, p = f.scale), "min_width" in f && e(18, h = f.min_width), "flex" in f && e(1, D = f.flex), "resizable" in f && e(19, b = f.resizable), "rtl" in f && e(20, v = f.rtl), "fullscreen" in f && e(0, C = f.fullscreen), "$$scope" in f && e(30, a = f.$$scope);
  }, s.$$.update = () => {
    s.$$.dirty[0] & /*fullscreen, old_fullscreen, element*/
    538968065 && C !== q && (e(29, q = C), C ? (e(24, K = T.getBoundingClientRect()), e(22, Q = T.offsetHeight), e(23, se = T.offsetWidth), window.addEventListener("keydown", V)) : (e(24, K = null), window.removeEventListener("keydown", V))), s.$$.dirty[0] & /*visible*/
    16384 && (d || e(1, D = !1));
  }, [
    C,
    D,
    o,
    i,
    r,
    l,
    m,
    g,
    F,
    u,
    $,
    w,
    y,
    x,
    d,
    c,
    _,
    p,
    h,
    b,
    v,
    T,
    Q,
    se,
    K,
    re,
    I,
    P,
    B,
    q,
    a,
    n,
    G
  ];
}
class Bt extends gt {
  constructor(t) {
    super(), bt(
      this,
      t,
      St,
      xt,
      kt,
      {
        height: 2,
        min_height: 3,
        max_height: 4,
        width: 5,
        elem_id: 6,
        elem_classes: 7,
        variant: 8,
        border_mode: 9,
        padding: 10,
        type: 28,
        test_id: 11,
        explicit_call: 12,
        container: 13,
        visible: 14,
        allow_overflow: 15,
        overflow_behavior: 16,
        scale: 17,
        min_width: 18,
        flex: 1,
        resizable: 19,
        rtl: 20,
        fullscreen: 0
      },
      null,
      [-1, -1]
    );
  }
}
function ke() {
  return {
    async: !1,
    breaks: !1,
    extensions: null,
    gfm: !0,
    hooks: null,
    pedantic: !1,
    renderer: null,
    silent: !1,
    tokenizer: null,
    walkTokens: null
  };
}
let Y = ke();
function et(s) {
  Y = s;
}
const tt = /[&<>"']/, qt = new RegExp(tt.source, "g"), nt = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, Tt = new RegExp(nt.source, "g"), It = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, Me = (s) => It[s];
function O(s, t) {
  if (t) {
    if (tt.test(s))
      return s.replace(qt, Me);
  } else if (nt.test(s))
    return s.replace(Tt, Me);
  return s;
}
const Rt = /&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig;
function zt(s) {
  return s.replace(Rt, (t, e) => (e = e.toLowerCase(), e === "colon" ? ":" : e.charAt(0) === "#" ? e.charAt(1) === "x" ? String.fromCharCode(parseInt(e.substring(2), 16)) : String.fromCharCode(+e.substring(1)) : ""));
}
const Lt = /(^|[^\[])\^/g;
function A(s, t) {
  let e = typeof s == "string" ? s : s.source;
  t = t || "";
  const n = {
    replace: (a, o) => {
      let i = typeof o == "string" ? o : o.source;
      return i = i.replace(Lt, "$1"), e = e.replace(a, i), n;
    },
    getRegex: () => new RegExp(e, t)
  };
  return n;
}
function Ne(s) {
  try {
    s = encodeURI(s).replace(/%25/g, "%");
  } catch {
    return null;
  }
  return s;
}
const te = { exec: () => null };
function He(s, t) {
  const e = s.replace(/\|/g, (o, i, r) => {
    let l = !1, m = i;
    for (; --m >= 0 && r[m] === "\\"; )
      l = !l;
    return l ? "|" : " |";
  }), n = e.split(/ \|/);
  let a = 0;
  if (n[0].trim() || n.shift(), n.length > 0 && !n[n.length - 1].trim() && n.pop(), t)
    if (n.length > t)
      n.splice(t);
    else
      for (; n.length < t; )
        n.push("");
  for (; a < n.length; a++)
    n[a] = n[a].trim().replace(/\\\|/g, "|");
  return n;
}
function _e(s, t, e) {
  const n = s.length;
  if (n === 0)
    return "";
  let a = 0;
  for (; a < n && s.charAt(n - a - 1) === t; )
    a++;
  return s.slice(0, n - a);
}
function Ot(s, t) {
  if (s.indexOf(t[1]) === -1)
    return -1;
  let e = 0;
  for (let n = 0; n < s.length; n++)
    if (s[n] === "\\")
      n++;
    else if (s[n] === t[0])
      e++;
    else if (s[n] === t[1] && (e--, e < 0))
      return n;
  return -1;
}
function je(s, t, e, n) {
  const a = t.href, o = t.title ? O(t.title) : null, i = s[1].replace(/\\([\[\]])/g, "$1");
  if (s[0].charAt(0) !== "!") {
    n.state.inLink = !0;
    const r = {
      type: "link",
      raw: e,
      href: a,
      title: o,
      text: i,
      tokens: n.inlineTokens(i)
    };
    return n.state.inLink = !1, r;
  }
  return {
    type: "image",
    raw: e,
    href: a,
    title: o,
    text: O(i)
  };
}
function Pt(s, t) {
  const e = s.match(/^(\s+)(?:```)/);
  if (e === null)
    return t;
  const n = e[1];
  return t.split(`
`).map((a) => {
    const o = a.match(/^\s+/);
    if (o === null)
      return a;
    const [i] = o;
    return i.length >= n.length ? a.slice(n.length) : a;
  }).join(`
`);
}
class he {
  // set by the lexer
  constructor(t) {
    S(this, "options");
    S(this, "rules");
    // set by the lexer
    S(this, "lexer");
    this.options = t || Y;
  }
  space(t) {
    const e = this.rules.block.newline.exec(t);
    if (e && e[0].length > 0)
      return {
        type: "space",
        raw: e[0]
      };
  }
  code(t) {
    const e = this.rules.block.code.exec(t);
    if (e) {
      const n = e[0].replace(/^ {1,4}/gm, "");
      return {
        type: "code",
        raw: e[0],
        codeBlockStyle: "indented",
        text: this.options.pedantic ? n : _e(n, `
`)
      };
    }
  }
  fences(t) {
    const e = this.rules.block.fences.exec(t);
    if (e) {
      const n = e[0], a = Pt(n, e[3] || "");
      return {
        type: "code",
        raw: n,
        lang: e[2] ? e[2].trim().replace(this.rules.inline.anyPunctuation, "$1") : e[2],
        text: a
      };
    }
  }
  heading(t) {
    const e = this.rules.block.heading.exec(t);
    if (e) {
      let n = e[2].trim();
      if (/#$/.test(n)) {
        const a = _e(n, "#");
        (this.options.pedantic || !a || / $/.test(a)) && (n = a.trim());
      }
      return {
        type: "heading",
        raw: e[0],
        depth: e[1].length,
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  hr(t) {
    const e = this.rules.block.hr.exec(t);
    if (e)
      return {
        type: "hr",
        raw: e[0]
      };
  }
  blockquote(t) {
    const e = this.rules.block.blockquote.exec(t);
    if (e) {
      let n = e[0].replace(/\n {0,3}((?:=+|-+) *)(?=\n|$)/g, `
    $1`);
      n = _e(n.replace(/^ *>[ \t]?/gm, ""), `
`);
      const a = this.lexer.state.top;
      this.lexer.state.top = !0;
      const o = this.lexer.blockTokens(n);
      return this.lexer.state.top = a, {
        type: "blockquote",
        raw: e[0],
        tokens: o,
        text: n
      };
    }
  }
  list(t) {
    let e = this.rules.block.list.exec(t);
    if (e) {
      let n = e[1].trim();
      const a = n.length > 1, o = {
        type: "list",
        raw: "",
        ordered: a,
        start: a ? +n.slice(0, -1) : "",
        loose: !1,
        items: []
      };
      n = a ? `\\d{1,9}\\${n.slice(-1)}` : `\\${n}`, this.options.pedantic && (n = a ? n : "[*+-]");
      const i = new RegExp(`^( {0,3}${n})((?:[	 ][^\\n]*)?(?:\\n|$))`);
      let r = "", l = "", m = !1;
      for (; t; ) {
        let g = !1;
        if (!(e = i.exec(t)) || this.rules.block.hr.test(t))
          break;
        r = e[0], t = t.substring(r.length);
        let F = e[2].split(`
`, 1)[0].replace(/^\t+/, (x) => " ".repeat(3 * x.length)), u = t.split(`
`, 1)[0], $ = 0;
        this.options.pedantic ? ($ = 2, l = F.trimStart()) : ($ = e[2].search(/[^ ]/), $ = $ > 4 ? 1 : $, l = F.slice($), $ += e[1].length);
        let B = !1;
        if (!F && /^ *$/.test(u) && (r += u + `
`, t = t.substring(u.length + 1), g = !0), !g) {
          const x = new RegExp(`^ {0,${Math.min(3, $ - 1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`), d = new RegExp(`^ {0,${Math.min(3, $ - 1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`), c = new RegExp(`^ {0,${Math.min(3, $ - 1)}}(?:\`\`\`|~~~)`), _ = new RegExp(`^ {0,${Math.min(3, $ - 1)}}#`);
          for (; t; ) {
            const p = t.split(`
`, 1)[0];
            if (u = p, this.options.pedantic && (u = u.replace(/^ {1,4}(?=( {4})*[^ ])/g, "  ")), c.test(u) || _.test(u) || x.test(u) || d.test(t))
              break;
            if (u.search(/[^ ]/) >= $ || !u.trim())
              l += `
` + u.slice($);
            else {
              if (B || F.search(/[^ ]/) >= 4 || c.test(F) || _.test(F) || d.test(F))
                break;
              l += `
` + u;
            }
            !B && !u.trim() && (B = !0), r += p + `
`, t = t.substring(p.length + 1), F = u.slice($);
          }
        }
        o.loose || (m ? o.loose = !0 : /\n *\n *$/.test(r) && (m = !0));
        let w = null, y;
        this.options.gfm && (w = /^\[[ xX]\] /.exec(l), w && (y = w[0] !== "[ ] ", l = l.replace(/^\[[ xX]\] +/, ""))), o.items.push({
          type: "list_item",
          raw: r,
          task: !!w,
          checked: y,
          loose: !1,
          text: l,
          tokens: []
        }), o.raw += r;
      }
      o.items[o.items.length - 1].raw = r.trimEnd(), o.items[o.items.length - 1].text = l.trimEnd(), o.raw = o.raw.trimEnd();
      for (let g = 0; g < o.items.length; g++)
        if (this.lexer.state.top = !1, o.items[g].tokens = this.lexer.blockTokens(o.items[g].text, []), !o.loose) {
          const F = o.items[g].tokens.filter(($) => $.type === "space"), u = F.length > 0 && F.some(($) => /\n.*\n/.test($.raw));
          o.loose = u;
        }
      if (o.loose)
        for (let g = 0; g < o.items.length; g++)
          o.items[g].loose = !0;
      return o;
    }
  }
  html(t) {
    const e = this.rules.block.html.exec(t);
    if (e)
      return {
        type: "html",
        block: !0,
        raw: e[0],
        pre: e[1] === "pre" || e[1] === "script" || e[1] === "style",
        text: e[0]
      };
  }
  def(t) {
    const e = this.rules.block.def.exec(t);
    if (e) {
      const n = e[1].toLowerCase().replace(/\s+/g, " "), a = e[2] ? e[2].replace(/^<(.*)>$/, "$1").replace(this.rules.inline.anyPunctuation, "$1") : "", o = e[3] ? e[3].substring(1, e[3].length - 1).replace(this.rules.inline.anyPunctuation, "$1") : e[3];
      return {
        type: "def",
        tag: n,
        raw: e[0],
        href: a,
        title: o
      };
    }
  }
  table(t) {
    const e = this.rules.block.table.exec(t);
    if (!e || !/[:|]/.test(e[2]))
      return;
    const n = He(e[1]), a = e[2].replace(/^\||\| *$/g, "").split("|"), o = e[3] && e[3].trim() ? e[3].replace(/\n[ \t]*$/, "").split(`
`) : [], i = {
      type: "table",
      raw: e[0],
      header: [],
      align: [],
      rows: []
    };
    if (n.length === a.length) {
      for (const r of a)
        /^ *-+: *$/.test(r) ? i.align.push("right") : /^ *:-+: *$/.test(r) ? i.align.push("center") : /^ *:-+ *$/.test(r) ? i.align.push("left") : i.align.push(null);
      for (const r of n)
        i.header.push({
          text: r,
          tokens: this.lexer.inline(r)
        });
      for (const r of o)
        i.rows.push(He(r, i.header.length).map((l) => ({
          text: l,
          tokens: this.lexer.inline(l)
        })));
      return i;
    }
  }
  lheading(t) {
    const e = this.rules.block.lheading.exec(t);
    if (e)
      return {
        type: "heading",
        raw: e[0],
        depth: e[2].charAt(0) === "=" ? 1 : 2,
        text: e[1],
        tokens: this.lexer.inline(e[1])
      };
  }
  paragraph(t) {
    const e = this.rules.block.paragraph.exec(t);
    if (e) {
      const n = e[1].charAt(e[1].length - 1) === `
` ? e[1].slice(0, -1) : e[1];
      return {
        type: "paragraph",
        raw: e[0],
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  text(t) {
    const e = this.rules.block.text.exec(t);
    if (e)
      return {
        type: "text",
        raw: e[0],
        text: e[0],
        tokens: this.lexer.inline(e[0])
      };
  }
  escape(t) {
    const e = this.rules.inline.escape.exec(t);
    if (e)
      return {
        type: "escape",
        raw: e[0],
        text: O(e[1])
      };
  }
  tag(t) {
    const e = this.rules.inline.tag.exec(t);
    if (e)
      return !this.lexer.state.inLink && /^<a /i.test(e[0]) ? this.lexer.state.inLink = !0 : this.lexer.state.inLink && /^<\/a>/i.test(e[0]) && (this.lexer.state.inLink = !1), !this.lexer.state.inRawBlock && /^<(pre|code|kbd|script)(\s|>)/i.test(e[0]) ? this.lexer.state.inRawBlock = !0 : this.lexer.state.inRawBlock && /^<\/(pre|code|kbd|script)(\s|>)/i.test(e[0]) && (this.lexer.state.inRawBlock = !1), {
        type: "html",
        raw: e[0],
        inLink: this.lexer.state.inLink,
        inRawBlock: this.lexer.state.inRawBlock,
        block: !1,
        text: e[0]
      };
  }
  link(t) {
    const e = this.rules.inline.link.exec(t);
    if (e) {
      const n = e[2].trim();
      if (!this.options.pedantic && /^</.test(n)) {
        if (!/>$/.test(n))
          return;
        const i = _e(n.slice(0, -1), "\\");
        if ((n.length - i.length) % 2 === 0)
          return;
      } else {
        const i = Ot(e[2], "()");
        if (i > -1) {
          const l = (e[0].indexOf("!") === 0 ? 5 : 4) + e[1].length + i;
          e[2] = e[2].substring(0, i), e[0] = e[0].substring(0, l).trim(), e[3] = "";
        }
      }
      let a = e[2], o = "";
      if (this.options.pedantic) {
        const i = /^([^'"]*[^\s])\s+(['"])(.*)\2/.exec(a);
        i && (a = i[1], o = i[3]);
      } else
        o = e[3] ? e[3].slice(1, -1) : "";
      return a = a.trim(), /^</.test(a) && (this.options.pedantic && !/>$/.test(n) ? a = a.slice(1) : a = a.slice(1, -1)), je(e, {
        href: a && a.replace(this.rules.inline.anyPunctuation, "$1"),
        title: o && o.replace(this.rules.inline.anyPunctuation, "$1")
      }, e[0], this.lexer);
    }
  }
  reflink(t, e) {
    let n;
    if ((n = this.rules.inline.reflink.exec(t)) || (n = this.rules.inline.nolink.exec(t))) {
      const a = (n[2] || n[1]).replace(/\s+/g, " "), o = e[a.toLowerCase()];
      if (!o) {
        const i = n[0].charAt(0);
        return {
          type: "text",
          raw: i,
          text: i
        };
      }
      return je(n, o, n[0], this.lexer);
    }
  }
  emStrong(t, e, n = "") {
    let a = this.rules.inline.emStrongLDelim.exec(t);
    if (!a || a[3] && n.match(/[\p{L}\p{N}]/u))
      return;
    if (!(a[1] || a[2] || "") || !n || this.rules.inline.punctuation.exec(n)) {
      const i = [...a[0]].length - 1;
      let r, l, m = i, g = 0;
      const F = a[0][0] === "*" ? this.rules.inline.emStrongRDelimAst : this.rules.inline.emStrongRDelimUnd;
      for (F.lastIndex = 0, e = e.slice(-1 * t.length + i); (a = F.exec(e)) != null; ) {
        if (r = a[1] || a[2] || a[3] || a[4] || a[5] || a[6], !r)
          continue;
        if (l = [...r].length, a[3] || a[4]) {
          m += l;
          continue;
        } else if ((a[5] || a[6]) && i % 3 && !((i + l) % 3)) {
          g += l;
          continue;
        }
        if (m -= l, m > 0)
          continue;
        l = Math.min(l, l + m + g);
        const u = [...a[0]][0].length, $ = t.slice(0, i + a.index + u + l);
        if (Math.min(i, l) % 2) {
          const w = $.slice(1, -1);
          return {
            type: "em",
            raw: $,
            text: w,
            tokens: this.lexer.inlineTokens(w)
          };
        }
        const B = $.slice(2, -2);
        return {
          type: "strong",
          raw: $,
          text: B,
          tokens: this.lexer.inlineTokens(B)
        };
      }
    }
  }
  codespan(t) {
    const e = this.rules.inline.code.exec(t);
    if (e) {
      let n = e[2].replace(/\n/g, " ");
      const a = /[^ ]/.test(n), o = /^ /.test(n) && / $/.test(n);
      return a && o && (n = n.substring(1, n.length - 1)), n = O(n, !0), {
        type: "codespan",
        raw: e[0],
        text: n
      };
    }
  }
  br(t) {
    const e = this.rules.inline.br.exec(t);
    if (e)
      return {
        type: "br",
        raw: e[0]
      };
  }
  del(t) {
    const e = this.rules.inline.del.exec(t);
    if (e)
      return {
        type: "del",
        raw: e[0],
        text: e[2],
        tokens: this.lexer.inlineTokens(e[2])
      };
  }
  autolink(t) {
    const e = this.rules.inline.autolink.exec(t);
    if (e) {
      let n, a;
      return e[2] === "@" ? (n = O(e[1]), a = "mailto:" + n) : (n = O(e[1]), a = n), {
        type: "link",
        raw: e[0],
        text: n,
        href: a,
        tokens: [
          {
            type: "text",
            raw: n,
            text: n
          }
        ]
      };
    }
  }
  url(t) {
    var n;
    let e;
    if (e = this.rules.inline.url.exec(t)) {
      let a, o;
      if (e[2] === "@")
        a = O(e[0]), o = "mailto:" + a;
      else {
        let i;
        do
          i = e[0], e[0] = ((n = this.rules.inline._backpedal.exec(e[0])) == null ? void 0 : n[0]) ?? "";
        while (i !== e[0]);
        a = O(e[0]), e[1] === "www." ? o = "http://" + e[0] : o = e[0];
      }
      return {
        type: "link",
        raw: e[0],
        text: a,
        href: o,
        tokens: [
          {
            type: "text",
            raw: a,
            text: a
          }
        ]
      };
    }
  }
  inlineText(t) {
    const e = this.rules.inline.text.exec(t);
    if (e) {
      let n;
      return this.lexer.state.inRawBlock ? n = e[0] : n = O(e[0]), {
        type: "text",
        raw: e[0],
        text: n
      };
    }
  }
}
const Mt = /^(?: *(?:\n|$))+/, Nt = /^( {4}[^\n]+(?:\n(?: *(?:\n|$))*)?)+/, Ht = /^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/, ae = /^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/, jt = /^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/, it = /(?:[*+-]|\d{1,9}[.)])/, at = A(/^(?!bull |blockCode|fences|blockquote|heading|html)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html))+?)\n {0,3}(=+|-+) *(?:\n+|$)/).replace(/bull/g, it).replace(/blockCode/g, / {4}/).replace(/fences/g, / {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g, / {0,3}>/).replace(/heading/g, / {0,3}#{1,6}/).replace(/html/g, / {0,3}<[^\n>]+>\n/).getRegex(), Ee = /^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/, Gt = /^[^\n]+/, Ae = /(?!\s*\])(?:\\.|[^\[\]\\])+/, Ut = A(/^ {0,3}\[(label)\]: *(?:\n *)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n *)?| *\n *)(title))? *(?:\n+|$)/).replace("label", Ae).replace("title", /(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(), Zt = A(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g, it).getRegex(), fe = "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul", xe = /<!--(?:-?>|[\s\S]*?(?:-->|$))/, Xt = A("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n *)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$))", "i").replace("comment", xe).replace("tag", fe).replace("attribute", / +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(), ot = A(Ee).replace("hr", ae).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("|table", "").replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", fe).getRegex(), Yt = A(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph", ot).getRegex(), Se = {
  blockquote: Yt,
  code: Nt,
  def: Ut,
  fences: Ht,
  heading: jt,
  hr: ae,
  html: Xt,
  lheading: at,
  list: Zt,
  newline: Mt,
  paragraph: ot,
  table: te,
  text: Gt
}, Ge = A("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr", ae).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("blockquote", " {0,3}>").replace("code", " {4}[^\\n]").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", fe).getRegex(), Wt = {
  ...Se,
  table: Ge,
  paragraph: A(Ee).replace("hr", ae).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("table", Ge).replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", fe).getRegex()
}, Qt = {
  ...Se,
  html: A(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment", xe).replace(/tag/g, "(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),
  def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,
  heading: /^(#{1,6})(.*)(?:\n+|$)/,
  fences: te,
  // fences not supported
  lheading: /^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,
  paragraph: A(Ee).replace("hr", ae).replace("heading", ` *#{1,6} *[^
]`).replace("lheading", at).replace("|table", "").replace("blockquote", " {0,3}>").replace("|fences", "").replace("|list", "").replace("|html", "").replace("|tag", "").getRegex()
}, rt = /^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/, Kt = /^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/, st = /^( {2,}|\\)\n(?!\s*$)/, Vt = /^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/, oe = "\\p{P}\\p{S}", Jt = A(/^((?![*_])[\spunctuation])/, "u").replace(/punctuation/g, oe).getRegex(), en = /\[[^[\]]*?\]\([^\(\)]*?\)|`[^`]*?`|<[^<>]*?>/g, tn = A(/^(?:\*+(?:((?!\*)[punct])|[^\s*]))|^_+(?:((?!_)[punct])|([^\s_]))/, "u").replace(/punct/g, oe).getRegex(), nn = A("^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)[punct](\\*+)(?=[\\s]|$)|[^punct\\s](\\*+)(?!\\*)(?=[punct\\s]|$)|(?!\\*)[punct\\s](\\*+)(?=[^punct\\s])|[\\s](\\*+)(?!\\*)(?=[punct])|(?!\\*)[punct](\\*+)(?!\\*)(?=[punct])|[^punct\\s](\\*+)(?=[^punct\\s])", "gu").replace(/punct/g, oe).getRegex(), an = A("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)[punct](_+)(?=[\\s]|$)|[^punct\\s](_+)(?!_)(?=[punct\\s]|$)|(?!_)[punct\\s](_+)(?=[^punct\\s])|[\\s](_+)(?!_)(?=[punct])|(?!_)[punct](_+)(?!_)(?=[punct])", "gu").replace(/punct/g, oe).getRegex(), on = A(/\\([punct])/, "gu").replace(/punct/g, oe).getRegex(), rn = A(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme", /[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email", /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(), sn = A(xe).replace("(?:-->|$)", "-->").getRegex(), ln = A("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment", sn).replace("attribute", /\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(), me = /(?:\[(?:\\.|[^\[\]\\])*\]|\\.|`[^`]*`|[^\[\]\\`])*?/, un = A(/^!?\[(label)\]\(\s*(href)(?:\s+(title))?\s*\)/).replace("label", me).replace("href", /<(?:\\.|[^\n<>\\])+>|[^\s\x00-\x1f]*/).replace("title", /"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(), lt = A(/^!?\[(label)\]\[(ref)\]/).replace("label", me).replace("ref", Ae).getRegex(), ut = A(/^!?\[(ref)\](?:\[\])?/).replace("ref", Ae).getRegex(), cn = A("reflink|nolink(?!\\()", "g").replace("reflink", lt).replace("nolink", ut).getRegex(), Be = {
  _backpedal: te,
  // only used for GFM url
  anyPunctuation: on,
  autolink: rn,
  blockSkip: en,
  br: st,
  code: Kt,
  del: te,
  emStrongLDelim: tn,
  emStrongRDelimAst: nn,
  emStrongRDelimUnd: an,
  escape: rt,
  link: un,
  nolink: ut,
  punctuation: Jt,
  reflink: lt,
  reflinkSearch: cn,
  tag: ln,
  text: Vt,
  url: te
}, dn = {
  ...Be,
  link: A(/^!?\[(label)\]\((.*?)\)/).replace("label", me).getRegex(),
  reflink: A(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label", me).getRegex()
}, we = {
  ...Be,
  escape: A(rt).replace("])", "~|])").getRegex(),
  url: A(/^((?:ftp|https?):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/, "i").replace("email", /[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),
  _backpedal: /(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,
  del: /^(~~?)(?=[^\s~])([\s\S]*?[^\s~])\1(?=[^~]|$)/,
  text: /^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|https?:\/\/|ftp:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/
}, _n = {
  ...we,
  br: A(st).replace("{2,}", "*").getRegex(),
  text: A(we.text).replace("\\b_", "\\b_| {2,}\\n").replace(/\{2,\}/g, "*").getRegex()
}, pe = {
  normal: Se,
  gfm: Wt,
  pedantic: Qt
}, J = {
  normal: Be,
  gfm: we,
  breaks: _n,
  pedantic: dn
};
class H {
  constructor(t) {
    S(this, "tokens");
    S(this, "options");
    S(this, "state");
    S(this, "tokenizer");
    S(this, "inlineQueue");
    this.tokens = [], this.tokens.links = /* @__PURE__ */ Object.create(null), this.options = t || Y, this.options.tokenizer = this.options.tokenizer || new he(), this.tokenizer = this.options.tokenizer, this.tokenizer.options = this.options, this.tokenizer.lexer = this, this.inlineQueue = [], this.state = {
      inLink: !1,
      inRawBlock: !1,
      top: !0
    };
    const e = {
      block: pe.normal,
      inline: J.normal
    };
    this.options.pedantic ? (e.block = pe.pedantic, e.inline = J.pedantic) : this.options.gfm && (e.block = pe.gfm, this.options.breaks ? e.inline = J.breaks : e.inline = J.gfm), this.tokenizer.rules = e;
  }
  /**
   * Expose Rules
   */
  static get rules() {
    return {
      block: pe,
      inline: J
    };
  }
  /**
   * Static Lex Method
   */
  static lex(t, e) {
    return new H(e).lex(t);
  }
  /**
   * Static Lex Inline Method
   */
  static lexInline(t, e) {
    return new H(e).inlineTokens(t);
  }
  /**
   * Preprocessing
   */
  lex(t) {
    t = t.replace(/\r\n|\r/g, `
`), this.blockTokens(t, this.tokens);
    for (let e = 0; e < this.inlineQueue.length; e++) {
      const n = this.inlineQueue[e];
      this.inlineTokens(n.src, n.tokens);
    }
    return this.inlineQueue = [], this.tokens;
  }
  blockTokens(t, e = []) {
    this.options.pedantic ? t = t.replace(/\t/g, "    ").replace(/^ +$/gm, "") : t = t.replace(/^( *)(\t+)/gm, (r, l, m) => l + "    ".repeat(m.length));
    let n, a, o, i;
    for (; t; )
      if (!(this.options.extensions && this.options.extensions.block && this.options.extensions.block.some((r) => (n = r.call({ lexer: this }, t, e)) ? (t = t.substring(n.raw.length), e.push(n), !0) : !1))) {
        if (n = this.tokenizer.space(t)) {
          t = t.substring(n.raw.length), n.raw.length === 1 && e.length > 0 ? e[e.length - 1].raw += `
` : e.push(n);
          continue;
        }
        if (n = this.tokenizer.code(t)) {
          t = t.substring(n.raw.length), a = e[e.length - 1], a && (a.type === "paragraph" || a.type === "text") ? (a.raw += `
` + n.raw, a.text += `
` + n.text, this.inlineQueue[this.inlineQueue.length - 1].src = a.text) : e.push(n);
          continue;
        }
        if (n = this.tokenizer.fences(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.heading(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.hr(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.blockquote(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.list(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.html(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.def(t)) {
          t = t.substring(n.raw.length), a = e[e.length - 1], a && (a.type === "paragraph" || a.type === "text") ? (a.raw += `
` + n.raw, a.text += `
` + n.raw, this.inlineQueue[this.inlineQueue.length - 1].src = a.text) : this.tokens.links[n.tag] || (this.tokens.links[n.tag] = {
            href: n.href,
            title: n.title
          });
          continue;
        }
        if (n = this.tokenizer.table(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.lheading(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (o = t, this.options.extensions && this.options.extensions.startBlock) {
          let r = 1 / 0;
          const l = t.slice(1);
          let m;
          this.options.extensions.startBlock.forEach((g) => {
            m = g.call({ lexer: this }, l), typeof m == "number" && m >= 0 && (r = Math.min(r, m));
          }), r < 1 / 0 && r >= 0 && (o = t.substring(0, r + 1));
        }
        if (this.state.top && (n = this.tokenizer.paragraph(o))) {
          a = e[e.length - 1], i && a.type === "paragraph" ? (a.raw += `
` + n.raw, a.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = a.text) : e.push(n), i = o.length !== t.length, t = t.substring(n.raw.length);
          continue;
        }
        if (n = this.tokenizer.text(t)) {
          t = t.substring(n.raw.length), a = e[e.length - 1], a && a.type === "text" ? (a.raw += `
` + n.raw, a.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = a.text) : e.push(n);
          continue;
        }
        if (t) {
          const r = "Infinite loop on byte: " + t.charCodeAt(0);
          if (this.options.silent) {
            console.error(r);
            break;
          } else
            throw new Error(r);
        }
      }
    return this.state.top = !0, e;
  }
  inline(t, e = []) {
    return this.inlineQueue.push({ src: t, tokens: e }), e;
  }
  /**
   * Lexing/Compiling
   */
  inlineTokens(t, e = []) {
    let n, a, o, i = t, r, l, m;
    if (this.tokens.links) {
      const g = Object.keys(this.tokens.links);
      if (g.length > 0)
        for (; (r = this.tokenizer.rules.inline.reflinkSearch.exec(i)) != null; )
          g.includes(r[0].slice(r[0].lastIndexOf("[") + 1, -1)) && (i = i.slice(0, r.index) + "[" + "a".repeat(r[0].length - 2) + "]" + i.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex));
    }
    for (; (r = this.tokenizer.rules.inline.blockSkip.exec(i)) != null; )
      i = i.slice(0, r.index) + "[" + "a".repeat(r[0].length - 2) + "]" + i.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);
    for (; (r = this.tokenizer.rules.inline.anyPunctuation.exec(i)) != null; )
      i = i.slice(0, r.index) + "++" + i.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);
    for (; t; )
      if (l || (m = ""), l = !1, !(this.options.extensions && this.options.extensions.inline && this.options.extensions.inline.some((g) => (n = g.call({ lexer: this }, t, e)) ? (t = t.substring(n.raw.length), e.push(n), !0) : !1))) {
        if (n = this.tokenizer.escape(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.tag(t)) {
          t = t.substring(n.raw.length), a = e[e.length - 1], a && n.type === "text" && a.type === "text" ? (a.raw += n.raw, a.text += n.text) : e.push(n);
          continue;
        }
        if (n = this.tokenizer.link(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.reflink(t, this.tokens.links)) {
          t = t.substring(n.raw.length), a = e[e.length - 1], a && n.type === "text" && a.type === "text" ? (a.raw += n.raw, a.text += n.text) : e.push(n);
          continue;
        }
        if (n = this.tokenizer.emStrong(t, i, m)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.codespan(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.br(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.del(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.autolink(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (!this.state.inLink && (n = this.tokenizer.url(t))) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (o = t, this.options.extensions && this.options.extensions.startInline) {
          let g = 1 / 0;
          const F = t.slice(1);
          let u;
          this.options.extensions.startInline.forEach(($) => {
            u = $.call({ lexer: this }, F), typeof u == "number" && u >= 0 && (g = Math.min(g, u));
          }), g < 1 / 0 && g >= 0 && (o = t.substring(0, g + 1));
        }
        if (n = this.tokenizer.inlineText(o)) {
          t = t.substring(n.raw.length), n.raw.slice(-1) !== "_" && (m = n.raw.slice(-1)), l = !0, a = e[e.length - 1], a && a.type === "text" ? (a.raw += n.raw, a.text += n.text) : e.push(n);
          continue;
        }
        if (t) {
          const g = "Infinite loop on byte: " + t.charCodeAt(0);
          if (this.options.silent) {
            console.error(g);
            break;
          } else
            throw new Error(g);
        }
      }
    return e;
  }
}
class ge {
  constructor(t) {
    S(this, "options");
    this.options = t || Y;
  }
  code(t, e, n) {
    var o;
    const a = (o = (e || "").match(/^\S*/)) == null ? void 0 : o[0];
    return t = t.replace(/\n$/, "") + `
`, a ? '<pre><code class="language-' + O(a) + '">' + (n ? t : O(t, !0)) + `</code></pre>
` : "<pre><code>" + (n ? t : O(t, !0)) + `</code></pre>
`;
  }
  blockquote(t) {
    return `<blockquote>
${t}</blockquote>
`;
  }
  html(t, e) {
    return t;
  }
  heading(t, e, n) {
    return `<h${e}>${t}</h${e}>
`;
  }
  hr() {
    return `<hr>
`;
  }
  list(t, e, n) {
    const a = e ? "ol" : "ul", o = e && n !== 1 ? ' start="' + n + '"' : "";
    return "<" + a + o + `>
` + t + "</" + a + `>
`;
  }
  listitem(t, e, n) {
    return `<li>${t}</li>
`;
  }
  checkbox(t) {
    return "<input " + (t ? 'checked="" ' : "") + 'disabled="" type="checkbox">';
  }
  paragraph(t) {
    return `<p>${t}</p>
`;
  }
  table(t, e) {
    return e && (e = `<tbody>${e}</tbody>`), `<table>
<thead>
` + t + `</thead>
` + e + `</table>
`;
  }
  tablerow(t) {
    return `<tr>
${t}</tr>
`;
  }
  tablecell(t, e) {
    const n = e.header ? "th" : "td";
    return (e.align ? `<${n} align="${e.align}">` : `<${n}>`) + t + `</${n}>
`;
  }
  /**
   * span level renderer
   */
  strong(t) {
    return `<strong>${t}</strong>`;
  }
  em(t) {
    return `<em>${t}</em>`;
  }
  codespan(t) {
    return `<code>${t}</code>`;
  }
  br() {
    return "<br>";
  }
  del(t) {
    return `<del>${t}</del>`;
  }
  link(t, e, n) {
    const a = Ne(t);
    if (a === null)
      return n;
    t = a;
    let o = '<a href="' + t + '"';
    return e && (o += ' title="' + e + '"'), o += ">" + n + "</a>", o;
  }
  image(t, e, n) {
    const a = Ne(t);
    if (a === null)
      return n;
    t = a;
    let o = `<img src="${t}" alt="${n}"`;
    return e && (o += ` title="${e}"`), o += ">", o;
  }
  text(t) {
    return t;
  }
}
class qe {
  // no need for block level renderers
  strong(t) {
    return t;
  }
  em(t) {
    return t;
  }
  codespan(t) {
    return t;
  }
  del(t) {
    return t;
  }
  html(t) {
    return t;
  }
  text(t) {
    return t;
  }
  link(t, e, n) {
    return "" + n;
  }
  image(t, e, n) {
    return "" + n;
  }
  br() {
    return "";
  }
}
class j {
  constructor(t) {
    S(this, "options");
    S(this, "renderer");
    S(this, "textRenderer");
    this.options = t || Y, this.options.renderer = this.options.renderer || new ge(), this.renderer = this.options.renderer, this.renderer.options = this.options, this.textRenderer = new qe();
  }
  /**
   * Static Parse Method
   */
  static parse(t, e) {
    return new j(e).parse(t);
  }
  /**
   * Static Parse Inline Method
   */
  static parseInline(t, e) {
    return new j(e).parseInline(t);
  }
  /**
   * Parse Loop
   */
  parse(t, e = !0) {
    let n = "";
    for (let a = 0; a < t.length; a++) {
      const o = t[a];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[o.type]) {
        const i = o, r = this.options.extensions.renderers[i.type].call({ parser: this }, i);
        if (r !== !1 || !["space", "hr", "heading", "code", "table", "blockquote", "list", "html", "paragraph", "text"].includes(i.type)) {
          n += r || "";
          continue;
        }
      }
      switch (o.type) {
        case "space":
          continue;
        case "hr": {
          n += this.renderer.hr();
          continue;
        }
        case "heading": {
          const i = o;
          n += this.renderer.heading(this.parseInline(i.tokens), i.depth, zt(this.parseInline(i.tokens, this.textRenderer)));
          continue;
        }
        case "code": {
          const i = o;
          n += this.renderer.code(i.text, i.lang, !!i.escaped);
          continue;
        }
        case "table": {
          const i = o;
          let r = "", l = "";
          for (let g = 0; g < i.header.length; g++)
            l += this.renderer.tablecell(this.parseInline(i.header[g].tokens), { header: !0, align: i.align[g] });
          r += this.renderer.tablerow(l);
          let m = "";
          for (let g = 0; g < i.rows.length; g++) {
            const F = i.rows[g];
            l = "";
            for (let u = 0; u < F.length; u++)
              l += this.renderer.tablecell(this.parseInline(F[u].tokens), { header: !1, align: i.align[u] });
            m += this.renderer.tablerow(l);
          }
          n += this.renderer.table(r, m);
          continue;
        }
        case "blockquote": {
          const i = o, r = this.parse(i.tokens);
          n += this.renderer.blockquote(r);
          continue;
        }
        case "list": {
          const i = o, r = i.ordered, l = i.start, m = i.loose;
          let g = "";
          for (let F = 0; F < i.items.length; F++) {
            const u = i.items[F], $ = u.checked, B = u.task;
            let w = "";
            if (u.task) {
              const y = this.renderer.checkbox(!!$);
              m ? u.tokens.length > 0 && u.tokens[0].type === "paragraph" ? (u.tokens[0].text = y + " " + u.tokens[0].text, u.tokens[0].tokens && u.tokens[0].tokens.length > 0 && u.tokens[0].tokens[0].type === "text" && (u.tokens[0].tokens[0].text = y + " " + u.tokens[0].tokens[0].text)) : u.tokens.unshift({
                type: "text",
                text: y + " "
              }) : w += y + " ";
            }
            w += this.parse(u.tokens, m), g += this.renderer.listitem(w, B, !!$);
          }
          n += this.renderer.list(g, r, l);
          continue;
        }
        case "html": {
          const i = o;
          n += this.renderer.html(i.text, i.block);
          continue;
        }
        case "paragraph": {
          const i = o;
          n += this.renderer.paragraph(this.parseInline(i.tokens));
          continue;
        }
        case "text": {
          let i = o, r = i.tokens ? this.parseInline(i.tokens) : i.text;
          for (; a + 1 < t.length && t[a + 1].type === "text"; )
            i = t[++a], r += `
` + (i.tokens ? this.parseInline(i.tokens) : i.text);
          n += e ? this.renderer.paragraph(r) : r;
          continue;
        }
        default: {
          const i = 'Token with "' + o.type + '" type was not found.';
          if (this.options.silent)
            return console.error(i), "";
          throw new Error(i);
        }
      }
    }
    return n;
  }
  /**
   * Parse Inline Tokens
   */
  parseInline(t, e) {
    e = e || this.renderer;
    let n = "";
    for (let a = 0; a < t.length; a++) {
      const o = t[a];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[o.type]) {
        const i = this.options.extensions.renderers[o.type].call({ parser: this }, o);
        if (i !== !1 || !["escape", "html", "link", "image", "strong", "em", "codespan", "br", "del", "text"].includes(o.type)) {
          n += i || "";
          continue;
        }
      }
      switch (o.type) {
        case "escape": {
          const i = o;
          n += e.text(i.text);
          break;
        }
        case "html": {
          const i = o;
          n += e.html(i.text);
          break;
        }
        case "link": {
          const i = o;
          n += e.link(i.href, i.title, this.parseInline(i.tokens, e));
          break;
        }
        case "image": {
          const i = o;
          n += e.image(i.href, i.title, i.text);
          break;
        }
        case "strong": {
          const i = o;
          n += e.strong(this.parseInline(i.tokens, e));
          break;
        }
        case "em": {
          const i = o;
          n += e.em(this.parseInline(i.tokens, e));
          break;
        }
        case "codespan": {
          const i = o;
          n += e.codespan(i.text);
          break;
        }
        case "br": {
          n += e.br();
          break;
        }
        case "del": {
          const i = o;
          n += e.del(this.parseInline(i.tokens, e));
          break;
        }
        case "text": {
          const i = o;
          n += e.text(i.text);
          break;
        }
        default: {
          const i = 'Token with "' + o.type + '" type was not found.';
          if (this.options.silent)
            return console.error(i), "";
          throw new Error(i);
        }
      }
    }
    return n;
  }
}
class ne {
  constructor(t) {
    S(this, "options");
    this.options = t || Y;
  }
  /**
   * Process markdown before marked
   */
  preprocess(t) {
    return t;
  }
  /**
   * Process HTML after marked is finished
   */
  postprocess(t) {
    return t;
  }
  /**
   * Process all tokens before walk tokens
   */
  processAllTokens(t) {
    return t;
  }
}
S(ne, "passThroughHooks", /* @__PURE__ */ new Set([
  "preprocess",
  "postprocess",
  "processAllTokens"
]));
var X, Ce, ct;
class pn {
  constructor(...t) {
    Re(this, X);
    S(this, "defaults", ke());
    S(this, "options", this.setOptions);
    S(this, "parse", de(this, X, Ce).call(this, H.lex, j.parse));
    S(this, "parseInline", de(this, X, Ce).call(this, H.lexInline, j.parseInline));
    S(this, "Parser", j);
    S(this, "Renderer", ge);
    S(this, "TextRenderer", qe);
    S(this, "Lexer", H);
    S(this, "Tokenizer", he);
    S(this, "Hooks", ne);
    this.use(...t);
  }
  /**
   * Run callback for every token
   */
  walkTokens(t, e) {
    var a, o;
    let n = [];
    for (const i of t)
      switch (n = n.concat(e.call(this, i)), i.type) {
        case "table": {
          const r = i;
          for (const l of r.header)
            n = n.concat(this.walkTokens(l.tokens, e));
          for (const l of r.rows)
            for (const m of l)
              n = n.concat(this.walkTokens(m.tokens, e));
          break;
        }
        case "list": {
          const r = i;
          n = n.concat(this.walkTokens(r.items, e));
          break;
        }
        default: {
          const r = i;
          (o = (a = this.defaults.extensions) == null ? void 0 : a.childTokens) != null && o[r.type] ? this.defaults.extensions.childTokens[r.type].forEach((l) => {
            const m = r[l].flat(1 / 0);
            n = n.concat(this.walkTokens(m, e));
          }) : r.tokens && (n = n.concat(this.walkTokens(r.tokens, e)));
        }
      }
    return n;
  }
  use(...t) {
    const e = this.defaults.extensions || { renderers: {}, childTokens: {} };
    return t.forEach((n) => {
      const a = { ...n };
      if (a.async = this.defaults.async || a.async || !1, n.extensions && (n.extensions.forEach((o) => {
        if (!o.name)
          throw new Error("extension name required");
        if ("renderer" in o) {
          const i = e.renderers[o.name];
          i ? e.renderers[o.name] = function(...r) {
            let l = o.renderer.apply(this, r);
            return l === !1 && (l = i.apply(this, r)), l;
          } : e.renderers[o.name] = o.renderer;
        }
        if ("tokenizer" in o) {
          if (!o.level || o.level !== "block" && o.level !== "inline")
            throw new Error("extension level must be 'block' or 'inline'");
          const i = e[o.level];
          i ? i.unshift(o.tokenizer) : e[o.level] = [o.tokenizer], o.start && (o.level === "block" ? e.startBlock ? e.startBlock.push(o.start) : e.startBlock = [o.start] : o.level === "inline" && (e.startInline ? e.startInline.push(o.start) : e.startInline = [o.start]));
        }
        "childTokens" in o && o.childTokens && (e.childTokens[o.name] = o.childTokens);
      }), a.extensions = e), n.renderer) {
        const o = this.defaults.renderer || new ge(this.defaults);
        for (const i in n.renderer) {
          if (!(i in o))
            throw new Error(`renderer '${i}' does not exist`);
          if (i === "options")
            continue;
          const r = i, l = n.renderer[r], m = o[r];
          o[r] = (...g) => {
            let F = l.apply(o, g);
            return F === !1 && (F = m.apply(o, g)), F || "";
          };
        }
        a.renderer = o;
      }
      if (n.tokenizer) {
        const o = this.defaults.tokenizer || new he(this.defaults);
        for (const i in n.tokenizer) {
          if (!(i in o))
            throw new Error(`tokenizer '${i}' does not exist`);
          if (["options", "rules", "lexer"].includes(i))
            continue;
          const r = i, l = n.tokenizer[r], m = o[r];
          o[r] = (...g) => {
            let F = l.apply(o, g);
            return F === !1 && (F = m.apply(o, g)), F;
          };
        }
        a.tokenizer = o;
      }
      if (n.hooks) {
        const o = this.defaults.hooks || new ne();
        for (const i in n.hooks) {
          if (!(i in o))
            throw new Error(`hook '${i}' does not exist`);
          if (i === "options")
            continue;
          const r = i, l = n.hooks[r], m = o[r];
          ne.passThroughHooks.has(i) ? o[r] = (g) => {
            if (this.defaults.async)
              return Promise.resolve(l.call(o, g)).then((u) => m.call(o, u));
            const F = l.call(o, g);
            return m.call(o, F);
          } : o[r] = (...g) => {
            let F = l.apply(o, g);
            return F === !1 && (F = m.apply(o, g)), F;
          };
        }
        a.hooks = o;
      }
      if (n.walkTokens) {
        const o = this.defaults.walkTokens, i = n.walkTokens;
        a.walkTokens = function(r) {
          let l = [];
          return l.push(i.call(this, r)), o && (l = l.concat(o.call(this, r))), l;
        };
      }
      this.defaults = { ...this.defaults, ...a };
    }), this;
  }
  setOptions(t) {
    return this.defaults = { ...this.defaults, ...t }, this;
  }
  lexer(t, e) {
    return H.lex(t, e ?? this.defaults);
  }
  parser(t, e) {
    return j.parse(t, e ?? this.defaults);
  }
}
X = new WeakSet(), Ce = function(t, e) {
  return (n, a) => {
    const o = { ...a }, i = { ...this.defaults, ...o };
    this.defaults.async === !0 && o.async === !1 && (i.silent || console.warn("marked(): The async option was set to true by an extension. The async: false option sent to parse will be ignored."), i.async = !0);
    const r = de(this, X, ct).call(this, !!i.silent, !!i.async);
    if (typeof n > "u" || n === null)
      return r(new Error("marked(): input parameter is undefined or null"));
    if (typeof n != "string")
      return r(new Error("marked(): input parameter is of type " + Object.prototype.toString.call(n) + ", string expected"));
    if (i.hooks && (i.hooks.options = i), i.async)
      return Promise.resolve(i.hooks ? i.hooks.preprocess(n) : n).then((l) => t(l, i)).then((l) => i.hooks ? i.hooks.processAllTokens(l) : l).then((l) => i.walkTokens ? Promise.all(this.walkTokens(l, i.walkTokens)).then(() => l) : l).then((l) => e(l, i)).then((l) => i.hooks ? i.hooks.postprocess(l) : l).catch(r);
    try {
      i.hooks && (n = i.hooks.preprocess(n));
      let l = t(n, i);
      i.hooks && (l = i.hooks.processAllTokens(l)), i.walkTokens && this.walkTokens(l, i.walkTokens);
      let m = e(l, i);
      return i.hooks && (m = i.hooks.postprocess(m)), m;
    } catch (l) {
      return r(l);
    }
  };
}, ct = function(t, e) {
  return (n) => {
    if (n.message += `
Please report this to https://github.com/markedjs/marked.`, t) {
      const a = "<p>An error occurred:</p><pre>" + O(n.message + "", !0) + "</pre>";
      return e ? Promise.resolve(a) : a;
    }
    if (e)
      return Promise.reject(n);
    throw n;
  };
};
const Z = new pn();
function E(s, t) {
  return Z.parse(s, t);
}
E.options = E.setOptions = function(s) {
  return Z.setOptions(s), E.defaults = Z.defaults, et(E.defaults), E;
};
E.getDefaults = ke;
E.defaults = Y;
E.use = function(...s) {
  return Z.use(...s), E.defaults = Z.defaults, et(E.defaults), E;
};
E.walkTokens = function(s, t) {
  return Z.walkTokens(s, t);
};
E.parseInline = Z.parseInline;
E.Parser = j;
E.parser = j.parse;
E.Renderer = ge;
E.TextRenderer = qe;
E.Lexer = H;
E.lexer = H.lex;
E.Tokenizer = he;
E.Hooks = ne;
E.parse = E;
E.options;
E.setOptions;
E.use;
E.walkTokens;
E.parseInline;
j.parse;
H.lex;
const hn = /[\0-\x1F!-,\.\/:-@\[-\^`\{-\xA9\xAB-\xB4\xB6-\xB9\xBB-\xBF\xD7\xF7\u02C2-\u02C5\u02D2-\u02DF\u02E5-\u02EB\u02ED\u02EF-\u02FF\u0375\u0378\u0379\u037E\u0380-\u0385\u0387\u038B\u038D\u03A2\u03F6\u0482\u0530\u0557\u0558\u055A-\u055F\u0589-\u0590\u05BE\u05C0\u05C3\u05C6\u05C8-\u05CF\u05EB-\u05EE\u05F3-\u060F\u061B-\u061F\u066A-\u066D\u06D4\u06DD\u06DE\u06E9\u06FD\u06FE\u0700-\u070F\u074B\u074C\u07B2-\u07BF\u07F6-\u07F9\u07FB\u07FC\u07FE\u07FF\u082E-\u083F\u085C-\u085F\u086B-\u089F\u08B5\u08C8-\u08D2\u08E2\u0964\u0965\u0970\u0984\u098D\u098E\u0991\u0992\u09A9\u09B1\u09B3-\u09B5\u09BA\u09BB\u09C5\u09C6\u09C9\u09CA\u09CF-\u09D6\u09D8-\u09DB\u09DE\u09E4\u09E5\u09F2-\u09FB\u09FD\u09FF\u0A00\u0A04\u0A0B-\u0A0E\u0A11\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A\u0A3B\u0A3D\u0A43-\u0A46\u0A49\u0A4A\u0A4E-\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA\u0ABB\u0AC6\u0ACA\u0ACE\u0ACF\u0AD1-\u0ADF\u0AE4\u0AE5\u0AF0-\u0AF8\u0B00\u0B04\u0B0D\u0B0E\u0B11\u0B12\u0B29\u0B31\u0B34\u0B3A\u0B3B\u0B45\u0B46\u0B49\u0B4A\u0B4E-\u0B54\u0B58-\u0B5B\u0B5E\u0B64\u0B65\u0B70\u0B72-\u0B81\u0B84\u0B8B-\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0-\u0BA2\u0BA5-\u0BA7\u0BAB-\u0BAD\u0BBA-\u0BBD\u0BC3-\u0BC5\u0BC9\u0BCE\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BF0-\u0BFF\u0C0D\u0C11\u0C29\u0C3A-\u0C3C\u0C45\u0C49\u0C4E-\u0C54\u0C57\u0C5B-\u0C5F\u0C64\u0C65\u0C70-\u0C7F\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA\u0CBB\u0CC5\u0CC9\u0CCE-\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4\u0CE5\u0CF0\u0CF3-\u0CFF\u0D0D\u0D11\u0D45\u0D49\u0D4F-\u0D53\u0D58-\u0D5E\u0D64\u0D65\u0D70-\u0D79\u0D80\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DE5\u0DF0\u0DF1\u0DF4-\u0E00\u0E3B-\u0E3F\u0E4F\u0E5A-\u0E80\u0E83\u0E85\u0E8B\u0EA4\u0EA6\u0EBE\u0EBF\u0EC5\u0EC7\u0ECE\u0ECF\u0EDA\u0EDB\u0EE0-\u0EFF\u0F01-\u0F17\u0F1A-\u0F1F\u0F2A-\u0F34\u0F36\u0F38\u0F3A-\u0F3D\u0F48\u0F6D-\u0F70\u0F85\u0F98\u0FBD-\u0FC5\u0FC7-\u0FFF\u104A-\u104F\u109E\u109F\u10C6\u10C8-\u10CC\u10CE\u10CF\u10FB\u1249\u124E\u124F\u1257\u1259\u125E\u125F\u1289\u128E\u128F\u12B1\u12B6\u12B7\u12BF\u12C1\u12C6\u12C7\u12D7\u1311\u1316\u1317\u135B\u135C\u1360-\u137F\u1390-\u139F\u13F6\u13F7\u13FE-\u1400\u166D\u166E\u1680\u169B-\u169F\u16EB-\u16ED\u16F9-\u16FF\u170D\u1715-\u171F\u1735-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17D4-\u17D6\u17D8-\u17DB\u17DE\u17DF\u17EA-\u180A\u180E\u180F\u181A-\u181F\u1879-\u187F\u18AB-\u18AF\u18F6-\u18FF\u191F\u192C-\u192F\u193C-\u1945\u196E\u196F\u1975-\u197F\u19AC-\u19AF\u19CA-\u19CF\u19DA-\u19FF\u1A1C-\u1A1F\u1A5F\u1A7D\u1A7E\u1A8A-\u1A8F\u1A9A-\u1AA6\u1AA8-\u1AAF\u1AC1-\u1AFF\u1B4C-\u1B4F\u1B5A-\u1B6A\u1B74-\u1B7F\u1BF4-\u1BFF\u1C38-\u1C3F\u1C4A-\u1C4C\u1C7E\u1C7F\u1C89-\u1C8F\u1CBB\u1CBC\u1CC0-\u1CCF\u1CD3\u1CFB-\u1CFF\u1DFA\u1F16\u1F17\u1F1E\u1F1F\u1F46\u1F47\u1F4E\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E\u1F7F\u1FB5\u1FBD\u1FBF-\u1FC1\u1FC5\u1FCD-\u1FCF\u1FD4\u1FD5\u1FDC-\u1FDF\u1FED-\u1FF1\u1FF5\u1FFD-\u203E\u2041-\u2053\u2055-\u2070\u2072-\u207E\u2080-\u208F\u209D-\u20CF\u20F1-\u2101\u2103-\u2106\u2108\u2109\u2114\u2116-\u2118\u211E-\u2123\u2125\u2127\u2129\u212E\u213A\u213B\u2140-\u2144\u214A-\u214D\u214F-\u215F\u2189-\u24B5\u24EA-\u2BFF\u2C2F\u2C5F\u2CE5-\u2CEA\u2CF4-\u2CFF\u2D26\u2D28-\u2D2C\u2D2E\u2D2F\u2D68-\u2D6E\u2D70-\u2D7E\u2D97-\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E00-\u2E2E\u2E30-\u3004\u3008-\u3020\u3030\u3036\u3037\u303D-\u3040\u3097\u3098\u309B\u309C\u30A0\u30FB\u3100-\u3104\u3130\u318F-\u319F\u31C0-\u31EF\u3200-\u33FF\u4DC0-\u4DFF\u9FFD-\u9FFF\uA48D-\uA4CF\uA4FE\uA4FF\uA60D-\uA60F\uA62C-\uA63F\uA673\uA67E\uA6F2-\uA716\uA720\uA721\uA789\uA78A\uA7C0\uA7C1\uA7CB-\uA7F4\uA828-\uA82B\uA82D-\uA83F\uA874-\uA87F\uA8C6-\uA8CF\uA8DA-\uA8DF\uA8F8-\uA8FA\uA8FC\uA92E\uA92F\uA954-\uA95F\uA97D-\uA97F\uA9C1-\uA9CE\uA9DA-\uA9DF\uA9FF\uAA37-\uAA3F\uAA4E\uAA4F\uAA5A-\uAA5F\uAA77-\uAA79\uAAC3-\uAADA\uAADE\uAADF\uAAF0\uAAF1\uAAF7-\uAB00\uAB07\uAB08\uAB0F\uAB10\uAB17-\uAB1F\uAB27\uAB2F\uAB5B\uAB6A-\uAB6F\uABEB\uABEE\uABEF\uABFA-\uABFF\uD7A4-\uD7AF\uD7C7-\uD7CA\uD7FC-\uD7FF\uE000-\uF8FF\uFA6E\uFA6F\uFADA-\uFAFF\uFB07-\uFB12\uFB18-\uFB1C\uFB29\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBB2-\uFBD2\uFD3E-\uFD4F\uFD90\uFD91\uFDC8-\uFDEF\uFDFC-\uFDFF\uFE10-\uFE1F\uFE30-\uFE32\uFE35-\uFE4C\uFE50-\uFE6F\uFE75\uFEFD-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF3E\uFF40\uFF5B-\uFF65\uFFBF-\uFFC1\uFFC8\uFFC9\uFFD0\uFFD1\uFFD8\uFFD9\uFFDD-\uFFFF]|\uD800[\uDC0C\uDC27\uDC3B\uDC3E\uDC4E\uDC4F\uDC5E-\uDC7F\uDCFB-\uDD3F\uDD75-\uDDFC\uDDFE-\uDE7F\uDE9D-\uDE9F\uDED1-\uDEDF\uDEE1-\uDEFF\uDF20-\uDF2C\uDF4B-\uDF4F\uDF7B-\uDF7F\uDF9E\uDF9F\uDFC4-\uDFC7\uDFD0\uDFD6-\uDFFF]|\uD801[\uDC9E\uDC9F\uDCAA-\uDCAF\uDCD4-\uDCD7\uDCFC-\uDCFF\uDD28-\uDD2F\uDD64-\uDDFF\uDF37-\uDF3F\uDF56-\uDF5F\uDF68-\uDFFF]|\uD802[\uDC06\uDC07\uDC09\uDC36\uDC39-\uDC3B\uDC3D\uDC3E\uDC56-\uDC5F\uDC77-\uDC7F\uDC9F-\uDCDF\uDCF3\uDCF6-\uDCFF\uDD16-\uDD1F\uDD3A-\uDD7F\uDDB8-\uDDBD\uDDC0-\uDDFF\uDE04\uDE07-\uDE0B\uDE14\uDE18\uDE36\uDE37\uDE3B-\uDE3E\uDE40-\uDE5F\uDE7D-\uDE7F\uDE9D-\uDEBF\uDEC8\uDEE7-\uDEFF\uDF36-\uDF3F\uDF56-\uDF5F\uDF73-\uDF7F\uDF92-\uDFFF]|\uD803[\uDC49-\uDC7F\uDCB3-\uDCBF\uDCF3-\uDCFF\uDD28-\uDD2F\uDD3A-\uDE7F\uDEAA\uDEAD-\uDEAF\uDEB2-\uDEFF\uDF1D-\uDF26\uDF28-\uDF2F\uDF51-\uDFAF\uDFC5-\uDFDF\uDFF7-\uDFFF]|\uD804[\uDC47-\uDC65\uDC70-\uDC7E\uDCBB-\uDCCF\uDCE9-\uDCEF\uDCFA-\uDCFF\uDD35\uDD40-\uDD43\uDD48-\uDD4F\uDD74\uDD75\uDD77-\uDD7F\uDDC5-\uDDC8\uDDCD\uDDDB\uDDDD-\uDDFF\uDE12\uDE38-\uDE3D\uDE3F-\uDE7F\uDE87\uDE89\uDE8E\uDE9E\uDEA9-\uDEAF\uDEEB-\uDEEF\uDEFA-\uDEFF\uDF04\uDF0D\uDF0E\uDF11\uDF12\uDF29\uDF31\uDF34\uDF3A\uDF45\uDF46\uDF49\uDF4A\uDF4E\uDF4F\uDF51-\uDF56\uDF58-\uDF5C\uDF64\uDF65\uDF6D-\uDF6F\uDF75-\uDFFF]|\uD805[\uDC4B-\uDC4F\uDC5A-\uDC5D\uDC62-\uDC7F\uDCC6\uDCC8-\uDCCF\uDCDA-\uDD7F\uDDB6\uDDB7\uDDC1-\uDDD7\uDDDE-\uDDFF\uDE41-\uDE43\uDE45-\uDE4F\uDE5A-\uDE7F\uDEB9-\uDEBF\uDECA-\uDEFF\uDF1B\uDF1C\uDF2C-\uDF2F\uDF3A-\uDFFF]|\uD806[\uDC3B-\uDC9F\uDCEA-\uDCFE\uDD07\uDD08\uDD0A\uDD0B\uDD14\uDD17\uDD36\uDD39\uDD3A\uDD44-\uDD4F\uDD5A-\uDD9F\uDDA8\uDDA9\uDDD8\uDDD9\uDDE2\uDDE5-\uDDFF\uDE3F-\uDE46\uDE48-\uDE4F\uDE9A-\uDE9C\uDE9E-\uDEBF\uDEF9-\uDFFF]|\uD807[\uDC09\uDC37\uDC41-\uDC4F\uDC5A-\uDC71\uDC90\uDC91\uDCA8\uDCB7-\uDCFF\uDD07\uDD0A\uDD37-\uDD39\uDD3B\uDD3E\uDD48-\uDD4F\uDD5A-\uDD5F\uDD66\uDD69\uDD8F\uDD92\uDD99-\uDD9F\uDDAA-\uDEDF\uDEF7-\uDFAF\uDFB1-\uDFFF]|\uD808[\uDF9A-\uDFFF]|\uD809[\uDC6F-\uDC7F\uDD44-\uDFFF]|[\uD80A\uD80B\uD80E-\uD810\uD812-\uD819\uD824-\uD82B\uD82D\uD82E\uD830-\uD833\uD837\uD839\uD83D\uD83F\uD87B-\uD87D\uD87F\uD885-\uDB3F\uDB41-\uDBFF][\uDC00-\uDFFF]|\uD80D[\uDC2F-\uDFFF]|\uD811[\uDE47-\uDFFF]|\uD81A[\uDE39-\uDE3F\uDE5F\uDE6A-\uDECF\uDEEE\uDEEF\uDEF5-\uDEFF\uDF37-\uDF3F\uDF44-\uDF4F\uDF5A-\uDF62\uDF78-\uDF7C\uDF90-\uDFFF]|\uD81B[\uDC00-\uDE3F\uDE80-\uDEFF\uDF4B-\uDF4E\uDF88-\uDF8E\uDFA0-\uDFDF\uDFE2\uDFE5-\uDFEF\uDFF2-\uDFFF]|\uD821[\uDFF8-\uDFFF]|\uD823[\uDCD6-\uDCFF\uDD09-\uDFFF]|\uD82C[\uDD1F-\uDD4F\uDD53-\uDD63\uDD68-\uDD6F\uDEFC-\uDFFF]|\uD82F[\uDC6B-\uDC6F\uDC7D-\uDC7F\uDC89-\uDC8F\uDC9A-\uDC9C\uDC9F-\uDFFF]|\uD834[\uDC00-\uDD64\uDD6A-\uDD6C\uDD73-\uDD7A\uDD83\uDD84\uDD8C-\uDDA9\uDDAE-\uDE41\uDE45-\uDFFF]|\uD835[\uDC55\uDC9D\uDCA0\uDCA1\uDCA3\uDCA4\uDCA7\uDCA8\uDCAD\uDCBA\uDCBC\uDCC4\uDD06\uDD0B\uDD0C\uDD15\uDD1D\uDD3A\uDD3F\uDD45\uDD47-\uDD49\uDD51\uDEA6\uDEA7\uDEC1\uDEDB\uDEFB\uDF15\uDF35\uDF4F\uDF6F\uDF89\uDFA9\uDFC3\uDFCC\uDFCD]|\uD836[\uDC00-\uDDFF\uDE37-\uDE3A\uDE6D-\uDE74\uDE76-\uDE83\uDE85-\uDE9A\uDEA0\uDEB0-\uDFFF]|\uD838[\uDC07\uDC19\uDC1A\uDC22\uDC25\uDC2B-\uDCFF\uDD2D-\uDD2F\uDD3E\uDD3F\uDD4A-\uDD4D\uDD4F-\uDEBF\uDEFA-\uDFFF]|\uD83A[\uDCC5-\uDCCF\uDCD7-\uDCFF\uDD4C-\uDD4F\uDD5A-\uDFFF]|\uD83B[\uDC00-\uDDFF\uDE04\uDE20\uDE23\uDE25\uDE26\uDE28\uDE33\uDE38\uDE3A\uDE3C-\uDE41\uDE43-\uDE46\uDE48\uDE4A\uDE4C\uDE50\uDE53\uDE55\uDE56\uDE58\uDE5A\uDE5C\uDE5E\uDE60\uDE63\uDE65\uDE66\uDE6B\uDE73\uDE78\uDE7D\uDE7F\uDE8A\uDE9C-\uDEA0\uDEA4\uDEAA\uDEBC-\uDFFF]|\uD83C[\uDC00-\uDD2F\uDD4A-\uDD4F\uDD6A-\uDD6F\uDD8A-\uDFFF]|\uD83E[\uDC00-\uDFEF\uDFFA-\uDFFF]|\uD869[\uDEDE-\uDEFF]|\uD86D[\uDF35-\uDF3F]|\uD86E[\uDC1E\uDC1F]|\uD873[\uDEA2-\uDEAF]|\uD87A[\uDFE1-\uDFFF]|\uD87E[\uDE1E-\uDFFF]|\uD884[\uDF4B-\uDFFF]|\uDB40[\uDC00-\uDCFF\uDDF0-\uDFFF]/g, mn = Object.hasOwnProperty;
class dt {
  /**
   * Create a new slug class.
   */
  constructor() {
    this.occurrences, this.reset();
  }
  /**
   * Generate a unique slug.
  *
  * Tracks previously generated slugs: repeated calls with the same value
  * will result in different slugs.
  * Use the `slug` function to get same slugs.
   *
   * @param  {string} value
   *   String of text to slugify
   * @param  {boolean} [maintainCase=false]
   *   Keep the current case, otherwise make all lowercase
   * @return {string}
   *   A unique slug string
   */
  slug(t, e) {
    const n = this;
    let a = gn(t, e === !0);
    const o = a;
    for (; mn.call(n.occurrences, a); )
      n.occurrences[o]++, a = o + "-" + n.occurrences[o];
    return n.occurrences[a] = 0, a;
  }
  /**
   * Reset - Forget all previous slugs
   *
   * @return void
   */
  reset() {
    this.occurrences = /* @__PURE__ */ Object.create(null);
  }
}
function gn(s, t) {
  return typeof s != "string" ? "" : (t || (s = s.toLowerCase()), s.replace(hn, "").replace(/ /g, "-"));
}
new dt();
var Ue = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, fn = { exports: {} };
(function(s) {
  var t = typeof window < "u" ? window : typeof WorkerGlobalScope < "u" && self instanceof WorkerGlobalScope ? self : {};
  /**
   * Prism: Lightweight, robust, elegant syntax highlighting
   *
   * @license MIT <https://opensource.org/licenses/MIT>
   * @author Lea Verou <https://lea.verou.me>
   * @namespace
   * @public
   */
  var e = function(n) {
    var a = /(?:^|\s)lang(?:uage)?-([\w-]+)(?=\s|$)/i, o = 0, i = {}, r = {
      /**
       * By default, Prism will attempt to highlight all code elements (by calling {@link Prism.highlightAll}) on the
       * current page after the page finished loading. This might be a problem if e.g. you wanted to asynchronously load
       * additional languages or plugins yourself.
       *
       * By setting this value to `true`, Prism will not automatically highlight all code elements on the page.
       *
       * You obviously have to change this value before the automatic highlighting started. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.manual = true;
       * // add a new <script> to load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      manual: n.Prism && n.Prism.manual,
      /**
       * By default, if Prism is in a web worker, it assumes that it is in a worker it created itself, so it uses
       * `addEventListener` to communicate with its parent instance. However, if you're using Prism manually in your
       * own worker, you don't want it to do this.
       *
       * By setting this value to `true`, Prism will not add its own listeners to the worker.
       *
       * You obviously have to change this value before Prism executes. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.disableWorkerMessageHandler = true;
       * // Load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      disableWorkerMessageHandler: n.Prism && n.Prism.disableWorkerMessageHandler,
      /**
       * A namespace for utility methods.
       *
       * All function in this namespace that are not explicitly marked as _public_ are for __internal use only__ and may
       * change or disappear at any time.
       *
       * @namespace
       * @memberof Prism
       */
      util: {
        encode: function d(c) {
          return c instanceof l ? new l(c.type, d(c.content), c.alias) : Array.isArray(c) ? c.map(d) : c.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/\u00a0/g, " ");
        },
        /**
         * Returns the name of the type of the given value.
         *
         * @param {any} o
         * @returns {string}
         * @example
         * type(null)      === 'Null'
         * type(undefined) === 'Undefined'
         * type(123)       === 'Number'
         * type('foo')     === 'String'
         * type(true)      === 'Boolean'
         * type([1, 2])    === 'Array'
         * type({})        === 'Object'
         * type(String)    === 'Function'
         * type(/abc+/)    === 'RegExp'
         */
        type: function(d) {
          return Object.prototype.toString.call(d).slice(8, -1);
        },
        /**
         * Returns a unique number for the given object. Later calls will still return the same number.
         *
         * @param {Object} obj
         * @returns {number}
         */
        objId: function(d) {
          return d.__id || Object.defineProperty(d, "__id", { value: ++o }), d.__id;
        },
        /**
         * Creates a deep clone of the given object.
         *
         * The main intended use of this function is to clone language definitions.
         *
         * @param {T} o
         * @param {Record<number, any>} [visited]
         * @returns {T}
         * @template T
         */
        clone: function d(c, _) {
          _ = _ || {};
          var p, h;
          switch (r.util.type(c)) {
            case "Object":
              if (h = r.util.objId(c), _[h])
                return _[h];
              p = /** @type {Record<string, any>} */
              {}, _[h] = p;
              for (var D in c)
                c.hasOwnProperty(D) && (p[D] = d(c[D], _));
              return (
                /** @type {any} */
                p
              );
            case "Array":
              return h = r.util.objId(c), _[h] ? _[h] : (p = [], _[h] = p, /** @type {Array} */
              /** @type {any} */
              c.forEach(function(b, v) {
                p[v] = d(b, _);
              }), /** @type {any} */
              p);
            default:
              return c;
          }
        },
        /**
         * Returns the Prism language of the given element set by a `language-xxxx` or `lang-xxxx` class.
         *
         * If no language is set for the element or the element is `null` or `undefined`, `none` will be returned.
         *
         * @param {Element} element
         * @returns {string}
         */
        getLanguage: function(d) {
          for (; d; ) {
            var c = a.exec(d.className);
            if (c)
              return c[1].toLowerCase();
            d = d.parentElement;
          }
          return "none";
        },
        /**
         * Sets the Prism `language-xxxx` class of the given element.
         *
         * @param {Element} element
         * @param {string} language
         * @returns {void}
         */
        setLanguage: function(d, c) {
          d.className = d.className.replace(RegExp(a, "gi"), ""), d.classList.add("language-" + c);
        },
        /**
         * Returns the script element that is currently executing.
         *
         * This does __not__ work for line script element.
         *
         * @returns {HTMLScriptElement | null}
         */
        currentScript: function() {
          if (typeof document > "u")
            return null;
          if ("currentScript" in document)
            return (
              /** @type {any} */
              document.currentScript
            );
          try {
            throw new Error();
          } catch (p) {
            var d = (/at [^(\r\n]*\((.*):[^:]+:[^:]+\)$/i.exec(p.stack) || [])[1];
            if (d) {
              var c = document.getElementsByTagName("script");
              for (var _ in c)
                if (c[_].src == d)
                  return c[_];
            }
            return null;
          }
        },
        /**
         * Returns whether a given class is active for `element`.
         *
         * The class can be activated if `element` or one of its ancestors has the given class and it can be deactivated
         * if `element` or one of its ancestors has the negated version of the given class. The _negated version_ of the
         * given class is just the given class with a `no-` prefix.
         *
         * Whether the class is active is determined by the closest ancestor of `element` (where `element` itself is
         * closest ancestor) that has the given class or the negated version of it. If neither `element` nor any of its
         * ancestors have the given class or the negated version of it, then the default activation will be returned.
         *
         * In the paradoxical situation where the closest ancestor contains __both__ the given class and the negated
         * version of it, the class is considered active.
         *
         * @param {Element} element
         * @param {string} className
         * @param {boolean} [defaultActivation=false]
         * @returns {boolean}
         */
        isActive: function(d, c, _) {
          for (var p = "no-" + c; d; ) {
            var h = d.classList;
            if (h.contains(c))
              return !0;
            if (h.contains(p))
              return !1;
            d = d.parentElement;
          }
          return !!_;
        }
      },
      /**
       * This namespace contains all currently loaded languages and the some helper functions to create and modify languages.
       *
       * @namespace
       * @memberof Prism
       * @public
       */
      languages: {
        /**
         * The grammar for plain, unformatted text.
         */
        plain: i,
        plaintext: i,
        text: i,
        txt: i,
        /**
         * Creates a deep copy of the language with the given id and appends the given tokens.
         *
         * If a token in `redef` also appears in the copied language, then the existing token in the copied language
         * will be overwritten at its original position.
         *
         * ## Best practices
         *
         * Since the position of overwriting tokens (token in `redef` that overwrite tokens in the copied language)
         * doesn't matter, they can technically be in any order. However, this can be confusing to others that trying to
         * understand the language definition because, normally, the order of tokens matters in Prism grammars.
         *
         * Therefore, it is encouraged to order overwriting tokens according to the positions of the overwritten tokens.
         * Furthermore, all non-overwriting tokens should be placed after the overwriting ones.
         *
         * @param {string} id The id of the language to extend. This has to be a key in `Prism.languages`.
         * @param {Grammar} redef The new tokens to append.
         * @returns {Grammar} The new language created.
         * @public
         * @example
         * Prism.languages['css-with-colors'] = Prism.languages.extend('css', {
         *     // Prism.languages.css already has a 'comment' token, so this token will overwrite CSS' 'comment' token
         *     // at its original position
         *     'comment': { ... },
         *     // CSS doesn't have a 'color' token, so this token will be appended
         *     'color': /\b(?:red|green|blue)\b/
         * });
         */
        extend: function(d, c) {
          var _ = r.util.clone(r.languages[d]);
          for (var p in c)
            _[p] = c[p];
          return _;
        },
        /**
         * Inserts tokens _before_ another token in a language definition or any other grammar.
         *
         * ## Usage
         *
         * This helper method makes it easy to modify existing languages. For example, the CSS language definition
         * not only defines CSS highlighting for CSS documents, but also needs to define highlighting for CSS embedded
         * in HTML through `<style>` elements. To do this, it needs to modify `Prism.languages.markup` and add the
         * appropriate tokens. However, `Prism.languages.markup` is a regular JavaScript object literal, so if you do
         * this:
         *
         * ```js
         * Prism.languages.markup.style = {
         *     // token
         * };
         * ```
         *
         * then the `style` token will be added (and processed) at the end. `insertBefore` allows you to insert tokens
         * before existing tokens. For the CSS example above, you would use it like this:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'cdata', {
         *     'style': {
         *         // token
         *     }
         * });
         * ```
         *
         * ## Special cases
         *
         * If the grammars of `inside` and `insert` have tokens with the same name, the tokens in `inside`'s grammar
         * will be ignored.
         *
         * This behavior can be used to insert tokens after `before`:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'comment', {
         *     'comment': Prism.languages.markup.comment,
         *     // tokens after 'comment'
         * });
         * ```
         *
         * ## Limitations
         *
         * The main problem `insertBefore` has to solve is iteration order. Since ES2015, the iteration order for object
         * properties is guaranteed to be the insertion order (except for integer keys) but some browsers behave
         * differently when keys are deleted and re-inserted. So `insertBefore` can't be implemented by temporarily
         * deleting properties which is necessary to insert at arbitrary positions.
         *
         * To solve this problem, `insertBefore` doesn't actually insert the given tokens into the target object.
         * Instead, it will create a new object and replace all references to the target object with the new one. This
         * can be done without temporarily deleting properties, so the iteration order is well-defined.
         *
         * However, only references that can be reached from `Prism.languages` or `insert` will be replaced. I.e. if
         * you hold the target object in a variable, then the value of the variable will not change.
         *
         * ```js
         * var oldMarkup = Prism.languages.markup;
         * var newMarkup = Prism.languages.insertBefore('markup', 'comment', { ... });
         *
         * assert(oldMarkup !== Prism.languages.markup);
         * assert(newMarkup === Prism.languages.markup);
         * ```
         *
         * @param {string} inside The property of `root` (e.g. a language id in `Prism.languages`) that contains the
         * object to be modified.
         * @param {string} before The key to insert before.
         * @param {Grammar} insert An object containing the key-value pairs to be inserted.
         * @param {Object<string, any>} [root] The object containing `inside`, i.e. the object that contains the
         * object to be modified.
         *
         * Defaults to `Prism.languages`.
         * @returns {Grammar} The new grammar object.
         * @public
         */
        insertBefore: function(d, c, _, p) {
          p = p || /** @type {any} */
          r.languages;
          var h = p[d], D = {};
          for (var b in h)
            if (h.hasOwnProperty(b)) {
              if (b == c)
                for (var v in _)
                  _.hasOwnProperty(v) && (D[v] = _[v]);
              _.hasOwnProperty(b) || (D[b] = h[b]);
            }
          var C = p[d];
          return p[d] = D, r.languages.DFS(r.languages, function(q, T) {
            T === C && q != d && (this[q] = D);
          }), D;
        },
        // Traverse a language definition with Depth First Search
        DFS: function d(c, _, p, h) {
          h = h || {};
          var D = r.util.objId;
          for (var b in c)
            if (c.hasOwnProperty(b)) {
              _.call(c, b, c[b], p || b);
              var v = c[b], C = r.util.type(v);
              C === "Object" && !h[D(v)] ? (h[D(v)] = !0, d(v, _, null, h)) : C === "Array" && !h[D(v)] && (h[D(v)] = !0, d(v, _, b, h));
            }
        }
      },
      plugins: {},
      /**
       * This is the most high-level function in Prism’s API.
       * It fetches all the elements that have a `.language-xxxx` class and then calls {@link Prism.highlightElement} on
       * each one of them.
       *
       * This is equivalent to `Prism.highlightAllUnder(document, async, callback)`.
       *
       * @param {boolean} [async=false] Same as in {@link Prism.highlightAllUnder}.
       * @param {HighlightCallback} [callback] Same as in {@link Prism.highlightAllUnder}.
       * @memberof Prism
       * @public
       */
      highlightAll: function(d, c) {
        r.highlightAllUnder(document, d, c);
      },
      /**
       * Fetches all the descendants of `container` that have a `.language-xxxx` class and then calls
       * {@link Prism.highlightElement} on each one of them.
       *
       * The following hooks will be run:
       * 1. `before-highlightall`
       * 2. `before-all-elements-highlight`
       * 3. All hooks of {@link Prism.highlightElement} for each element.
       *
       * @param {ParentNode} container The root element, whose descendants that have a `.language-xxxx` class will be highlighted.
       * @param {boolean} [async=false] Whether each element is to be highlighted asynchronously using Web Workers.
       * @param {HighlightCallback} [callback] An optional callback to be invoked on each element after its highlighting is done.
       * @memberof Prism
       * @public
       */
      highlightAllUnder: function(d, c, _) {
        var p = {
          callback: _,
          container: d,
          selector: 'code[class*="language-"], [class*="language-"] code, code[class*="lang-"], [class*="lang-"] code'
        };
        r.hooks.run("before-highlightall", p), p.elements = Array.prototype.slice.apply(p.container.querySelectorAll(p.selector)), r.hooks.run("before-all-elements-highlight", p);
        for (var h = 0, D; D = p.elements[h++]; )
          r.highlightElement(D, c === !0, p.callback);
      },
      /**
       * Highlights the code inside a single element.
       *
       * The following hooks will be run:
       * 1. `before-sanity-check`
       * 2. `before-highlight`
       * 3. All hooks of {@link Prism.highlight}. These hooks will be run by an asynchronous worker if `async` is `true`.
       * 4. `before-insert`
       * 5. `after-highlight`
       * 6. `complete`
       *
       * Some the above hooks will be skipped if the element doesn't contain any text or there is no grammar loaded for
       * the element's language.
       *
       * @param {Element} element The element containing the code.
       * It must have a class of `language-xxxx` to be processed, where `xxxx` is a valid language identifier.
       * @param {boolean} [async=false] Whether the element is to be highlighted asynchronously using Web Workers
       * to improve performance and avoid blocking the UI when highlighting very large chunks of code. This option is
       * [disabled by default](https://prismjs.com/faq.html#why-is-asynchronous-highlighting-disabled-by-default).
       *
       * Note: All language definitions required to highlight the code must be included in the main `prism.js` file for
       * asynchronous highlighting to work. You can build your own bundle on the
       * [Download page](https://prismjs.com/download.html).
       * @param {HighlightCallback} [callback] An optional callback to be invoked after the highlighting is done.
       * Mostly useful when `async` is `true`, since in that case, the highlighting is done asynchronously.
       * @memberof Prism
       * @public
       */
      highlightElement: function(d, c, _) {
        var p = r.util.getLanguage(d), h = r.languages[p];
        r.util.setLanguage(d, p);
        var D = d.parentElement;
        D && D.nodeName.toLowerCase() === "pre" && r.util.setLanguage(D, p);
        var b = d.textContent, v = {
          element: d,
          language: p,
          grammar: h,
          code: b
        };
        function C(T) {
          v.highlightedCode = T, r.hooks.run("before-insert", v), v.element.innerHTML = v.highlightedCode, r.hooks.run("after-highlight", v), r.hooks.run("complete", v), _ && _.call(v.element);
        }
        if (r.hooks.run("before-sanity-check", v), D = v.element.parentElement, D && D.nodeName.toLowerCase() === "pre" && !D.hasAttribute("tabindex") && D.setAttribute("tabindex", "0"), !v.code) {
          r.hooks.run("complete", v), _ && _.call(v.element);
          return;
        }
        if (r.hooks.run("before-highlight", v), !v.grammar) {
          C(r.util.encode(v.code));
          return;
        }
        if (c && n.Worker) {
          var q = new Worker(r.filename);
          q.onmessage = function(T) {
            C(T.data);
          }, q.postMessage(JSON.stringify({
            language: v.language,
            code: v.code,
            immediateClose: !0
          }));
        } else
          C(r.highlight(v.code, v.grammar, v.language));
      },
      /**
       * Low-level function, only use if you know what you’re doing. It accepts a string of text as input
       * and the language definitions to use, and returns a string with the HTML produced.
       *
       * The following hooks will be run:
       * 1. `before-tokenize`
       * 2. `after-tokenize`
       * 3. `wrap`: On each {@link Token}.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @param {string} language The name of the language definition passed to `grammar`.
       * @returns {string} The highlighted HTML.
       * @memberof Prism
       * @public
       * @example
       * Prism.highlight('var foo = true;', Prism.languages.javascript, 'javascript');
       */
      highlight: function(d, c, _) {
        var p = {
          code: d,
          grammar: c,
          language: _
        };
        if (r.hooks.run("before-tokenize", p), !p.grammar)
          throw new Error('The language "' + p.language + '" has no grammar.');
        return p.tokens = r.tokenize(p.code, p.grammar), r.hooks.run("after-tokenize", p), l.stringify(r.util.encode(p.tokens), p.language);
      },
      /**
       * This is the heart of Prism, and the most low-level function you can use. It accepts a string of text as input
       * and the language definitions to use, and returns an array with the tokenized code.
       *
       * When the language definition includes nested tokens, the function is called recursively on each of these tokens.
       *
       * This method could be useful in other contexts as well, as a very crude parser.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @returns {TokenStream} An array of strings and tokens, a token stream.
       * @memberof Prism
       * @public
       * @example
       * let code = `var foo = 0;`;
       * let tokens = Prism.tokenize(code, Prism.languages.javascript);
       * tokens.forEach(token => {
       *     if (token instanceof Prism.Token && token.type === 'number') {
       *         console.log(`Found numeric literal: ${token.content}`);
       *     }
       * });
       */
      tokenize: function(d, c) {
        var _ = c.rest;
        if (_) {
          for (var p in _)
            c[p] = _[p];
          delete c.rest;
        }
        var h = new F();
        return u(h, h.head, d), g(d, h, c, h.head, 0), B(h);
      },
      /**
       * @namespace
       * @memberof Prism
       * @public
       */
      hooks: {
        all: {},
        /**
         * Adds the given callback to the list of callbacks for the given hook.
         *
         * The callback will be invoked when the hook it is registered for is run.
         * Hooks are usually directly run by a highlight function but you can also run hooks yourself.
         *
         * One callback function can be registered to multiple hooks and the same hook multiple times.
         *
         * @param {string} name The name of the hook.
         * @param {HookCallback} callback The callback function which is given environment variables.
         * @public
         */
        add: function(d, c) {
          var _ = r.hooks.all;
          _[d] = _[d] || [], _[d].push(c);
        },
        /**
         * Runs a hook invoking all registered callbacks with the given environment variables.
         *
         * Callbacks will be invoked synchronously and in the order in which they were registered.
         *
         * @param {string} name The name of the hook.
         * @param {Object<string, any>} env The environment variables of the hook passed to all callbacks registered.
         * @public
         */
        run: function(d, c) {
          var _ = r.hooks.all[d];
          if (!(!_ || !_.length))
            for (var p = 0, h; h = _[p++]; )
              h(c);
        }
      },
      Token: l
    };
    n.Prism = r;
    function l(d, c, _, p) {
      this.type = d, this.content = c, this.alias = _, this.length = (p || "").length | 0;
    }
    l.stringify = function d(c, _) {
      if (typeof c == "string")
        return c;
      if (Array.isArray(c)) {
        var p = "";
        return c.forEach(function(C) {
          p += d(C, _);
        }), p;
      }
      var h = {
        type: c.type,
        content: d(c.content, _),
        tag: "span",
        classes: ["token", c.type],
        attributes: {},
        language: _
      }, D = c.alias;
      D && (Array.isArray(D) ? Array.prototype.push.apply(h.classes, D) : h.classes.push(D)), r.hooks.run("wrap", h);
      var b = "";
      for (var v in h.attributes)
        b += " " + v + '="' + (h.attributes[v] || "").replace(/"/g, "&quot;") + '"';
      return "<" + h.tag + ' class="' + h.classes.join(" ") + '"' + b + ">" + h.content + "</" + h.tag + ">";
    };
    function m(d, c, _, p) {
      d.lastIndex = c;
      var h = d.exec(_);
      if (h && p && h[1]) {
        var D = h[1].length;
        h.index += D, h[0] = h[0].slice(D);
      }
      return h;
    }
    function g(d, c, _, p, h, D) {
      for (var b in _)
        if (!(!_.hasOwnProperty(b) || !_[b])) {
          var v = _[b];
          v = Array.isArray(v) ? v : [v];
          for (var C = 0; C < v.length; ++C) {
            if (D && D.cause == b + "," + C)
              return;
            var q = v[C], T = q.inside, re = !!q.lookbehind, Q = !!q.greedy, se = q.alias;
            if (Q && !q.pattern.global) {
              var K = q.pattern.toString().match(/[imsuy]*$/)[0];
              q.pattern = RegExp(q.pattern.source, K + "g");
            }
            for (var V = q.pattern || q, I = p.next, P = h; I !== c.tail && !(D && P >= D.reach); P += I.value.length, I = I.next) {
              var G = I.value;
              if (c.length > d.length)
                return;
              if (!(G instanceof l)) {
                var f = 1, L;
                if (Q) {
                  if (L = m(V, P, d, re), !L || L.index >= d.length)
                    break;
                  var W = L.index, le = L.index + L[0].length, M = P;
                  for (M += I.value.length; W >= M; )
                    I = I.next, M += I.value.length;
                  if (M -= I.value.length, P = M, I.value instanceof l)
                    continue;
                  for (var U = I; U !== c.tail && (M < le || typeof U.value == "string"); U = U.next)
                    f++, M += U.value.length;
                  f--, G = d.slice(P, M), L.index -= P;
                } else if (L = m(V, 0, G, re), !L)
                  continue;
                var W = L.index, ue = L[0], $e = G.slice(0, W), Te = G.slice(W + ue.length), De = P + G.length;
                D && De > D.reach && (D.reach = De);
                var ce = I.prev;
                $e && (ce = u(c, ce, $e), P += $e.length), $(c, ce, f);
                var _t = new l(b, T ? r.tokenize(ue, T) : ue, se, ue);
                if (I = u(c, ce, _t), Te && u(c, I, Te), f > 1) {
                  var ve = {
                    cause: b + "," + C,
                    reach: De
                  };
                  g(d, c, _, I.prev, P, ve), D && ve.reach > D.reach && (D.reach = ve.reach);
                }
              }
            }
          }
        }
    }
    function F() {
      var d = { value: null, prev: null, next: null }, c = { value: null, prev: d, next: null };
      d.next = c, this.head = d, this.tail = c, this.length = 0;
    }
    function u(d, c, _) {
      var p = c.next, h = { value: _, prev: c, next: p };
      return c.next = h, p.prev = h, d.length++, h;
    }
    function $(d, c, _) {
      for (var p = c.next, h = 0; h < _ && p !== d.tail; h++)
        p = p.next;
      c.next = p, p.prev = c, d.length -= h;
    }
    function B(d) {
      for (var c = [], _ = d.head.next; _ !== d.tail; )
        c.push(_.value), _ = _.next;
      return c;
    }
    if (!n.document)
      return n.addEventListener && (r.disableWorkerMessageHandler || n.addEventListener("message", function(d) {
        var c = JSON.parse(d.data), _ = c.language, p = c.code, h = c.immediateClose;
        n.postMessage(r.highlight(p, r.languages[_], _)), h && n.close();
      }, !1)), r;
    var w = r.util.currentScript();
    w && (r.filename = w.src, w.hasAttribute("data-manual") && (r.manual = !0));
    function y() {
      r.manual || r.highlightAll();
    }
    if (!r.manual) {
      var x = document.readyState;
      x === "loading" || x === "interactive" && w && w.defer ? document.addEventListener("DOMContentLoaded", y) : window.requestAnimationFrame ? window.requestAnimationFrame(y) : window.setTimeout(y, 16);
    }
    return r;
  }(t);
  s.exports && (s.exports = e), typeof Ue < "u" && (Ue.Prism = e), e.languages.markup = {
    comment: {
      pattern: /<!--(?:(?!<!--)[\s\S])*?-->/,
      greedy: !0
    },
    prolog: {
      pattern: /<\?[\s\S]+?\?>/,
      greedy: !0
    },
    doctype: {
      // https://www.w3.org/TR/xml/#NT-doctypedecl
      pattern: /<!DOCTYPE(?:[^>"'[\]]|"[^"]*"|'[^']*')+(?:\[(?:[^<"'\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\]\s*)?>/i,
      greedy: !0,
      inside: {
        "internal-subset": {
          pattern: /(^[^\[]*\[)[\s\S]+(?=\]>$)/,
          lookbehind: !0,
          greedy: !0,
          inside: null
          // see below
        },
        string: {
          pattern: /"[^"]*"|'[^']*'/,
          greedy: !0
        },
        punctuation: /^<!|>$|[[\]]/,
        "doctype-tag": /^DOCTYPE/i,
        name: /[^\s<>'"]+/
      }
    },
    cdata: {
      pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
      greedy: !0
    },
    tag: {
      pattern: /<\/?(?!\d)[^\s>\/=$<%]+(?:\s(?:\s*[^\s>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))|(?=[\s/>])))+)?\s*\/?>/,
      greedy: !0,
      inside: {
        tag: {
          pattern: /^<\/?[^\s>\/]+/,
          inside: {
            punctuation: /^<\/?/,
            namespace: /^[^\s>\/:]+:/
          }
        },
        "special-attr": [],
        "attr-value": {
          pattern: /=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+)/,
          inside: {
            punctuation: [
              {
                pattern: /^=/,
                alias: "attr-equals"
              },
              {
                pattern: /^(\s*)["']|["']$/,
                lookbehind: !0
              }
            ]
          }
        },
        punctuation: /\/?>/,
        "attr-name": {
          pattern: /[^\s>\/]+/,
          inside: {
            namespace: /^[^\s>\/:]+:/
          }
        }
      }
    },
    entity: [
      {
        pattern: /&[\da-z]{1,8};/i,
        alias: "named-entity"
      },
      /&#x?[\da-f]{1,8};/i
    ]
  }, e.languages.markup.tag.inside["attr-value"].inside.entity = e.languages.markup.entity, e.languages.markup.doctype.inside["internal-subset"].inside = e.languages.markup, e.hooks.add("wrap", function(n) {
    n.type === "entity" && (n.attributes.title = n.content.replace(/&amp;/, "&"));
  }), Object.defineProperty(e.languages.markup.tag, "addInlined", {
    /**
     * Adds an inlined language to markup.
     *
     * An example of an inlined language is CSS with `<style>` tags.
     *
     * @param {string} tagName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addInlined('style', 'css');
     */
    value: function(a, o) {
      var i = {};
      i["language-" + o] = {
        pattern: /(^<!\[CDATA\[)[\s\S]+?(?=\]\]>$)/i,
        lookbehind: !0,
        inside: e.languages[o]
      }, i.cdata = /^<!\[CDATA\[|\]\]>$/i;
      var r = {
        "included-cdata": {
          pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
          inside: i
        }
      };
      r["language-" + o] = {
        pattern: /[\s\S]+/,
        inside: e.languages[o]
      };
      var l = {};
      l[a] = {
        pattern: RegExp(/(<__[^>]*>)(?:<!\[CDATA\[(?:[^\]]|\](?!\]>))*\]\]>|(?!<!\[CDATA\[)[\s\S])*?(?=<\/__>)/.source.replace(/__/g, function() {
          return a;
        }), "i"),
        lookbehind: !0,
        greedy: !0,
        inside: r
      }, e.languages.insertBefore("markup", "cdata", l);
    }
  }), Object.defineProperty(e.languages.markup.tag, "addAttribute", {
    /**
     * Adds an pattern to highlight languages embedded in HTML attributes.
     *
     * An example of an inlined language is CSS with `style` attributes.
     *
     * @param {string} attrName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addAttribute('style', 'css');
     */
    value: function(n, a) {
      e.languages.markup.tag.inside["special-attr"].push({
        pattern: RegExp(
          /(^|["'\s])/.source + "(?:" + n + ")" + /\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))/.source,
          "i"
        ),
        lookbehind: !0,
        inside: {
          "attr-name": /^[^\s=]+/,
          "attr-value": {
            pattern: /=[\s\S]+/,
            inside: {
              value: {
                pattern: /(^=\s*(["']|(?!["'])))\S[\s\S]*(?=\2$)/,
                lookbehind: !0,
                alias: [a, "language-" + a],
                inside: e.languages[a]
              },
              punctuation: [
                {
                  pattern: /^=/,
                  alias: "attr-equals"
                },
                /"|'/
              ]
            }
          }
        }
      });
    }
  }), e.languages.html = e.languages.markup, e.languages.mathml = e.languages.markup, e.languages.svg = e.languages.markup, e.languages.xml = e.languages.extend("markup", {}), e.languages.ssml = e.languages.xml, e.languages.atom = e.languages.xml, e.languages.rss = e.languages.xml, function(n) {
    var a = /(?:"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n])*')/;
    n.languages.css = {
      comment: /\/\*[\s\S]*?\*\//,
      atrule: {
        pattern: RegExp("@[\\w-](?:" + /[^;{\s"']|\s+(?!\s)/.source + "|" + a.source + ")*?" + /(?:;|(?=\s*\{))/.source),
        inside: {
          rule: /^@[\w-]+/,
          "selector-function-argument": {
            pattern: /(\bselector\s*\(\s*(?![\s)]))(?:[^()\s]|\s+(?![\s)])|\((?:[^()]|\([^()]*\))*\))+(?=\s*\))/,
            lookbehind: !0,
            alias: "selector"
          },
          keyword: {
            pattern: /(^|[^\w-])(?:and|not|only|or)(?![\w-])/,
            lookbehind: !0
          }
          // See rest below
        }
      },
      url: {
        // https://drafts.csswg.org/css-values-3/#urls
        pattern: RegExp("\\burl\\((?:" + a.source + "|" + /(?:[^\\\r\n()"']|\\[\s\S])*/.source + ")\\)", "i"),
        greedy: !0,
        inside: {
          function: /^url/i,
          punctuation: /^\(|\)$/,
          string: {
            pattern: RegExp("^" + a.source + "$"),
            alias: "url"
          }
        }
      },
      selector: {
        pattern: RegExp(`(^|[{}\\s])[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|` + a.source + ")*(?=\\s*\\{)"),
        lookbehind: !0
      },
      string: {
        pattern: a,
        greedy: !0
      },
      property: {
        pattern: /(^|[^-\w\xA0-\uFFFF])(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*(?=\s*:)/i,
        lookbehind: !0
      },
      important: /!important\b/i,
      function: {
        pattern: /(^|[^-a-z0-9])[-a-z0-9]+(?=\()/i,
        lookbehind: !0
      },
      punctuation: /[(){};:,]/
    }, n.languages.css.atrule.inside.rest = n.languages.css;
    var o = n.languages.markup;
    o && (o.tag.addInlined("style", "css"), o.tag.addAttribute("style", "css"));
  }(e), e.languages.clike = {
    comment: [
      {
        pattern: /(^|[^\\])\/\*[\s\S]*?(?:\*\/|$)/,
        lookbehind: !0,
        greedy: !0
      },
      {
        pattern: /(^|[^\\:])\/\/.*/,
        lookbehind: !0,
        greedy: !0
      }
    ],
    string: {
      pattern: /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
      greedy: !0
    },
    "class-name": {
      pattern: /(\b(?:class|extends|implements|instanceof|interface|new|trait)\s+|\bcatch\s+\()[\w.\\]+/i,
      lookbehind: !0,
      inside: {
        punctuation: /[.\\]/
      }
    },
    keyword: /\b(?:break|catch|continue|do|else|finally|for|function|if|in|instanceof|new|null|return|throw|try|while)\b/,
    boolean: /\b(?:false|true)\b/,
    function: /\b\w+(?=\()/,
    number: /\b0x[\da-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?/i,
    operator: /[<>]=?|[!=]=?=?|--?|\+\+?|&&?|\|\|?|[?*/~^%]/,
    punctuation: /[{}[\];(),.:]/
  }, e.languages.javascript = e.languages.extend("clike", {
    "class-name": [
      e.languages.clike["class-name"],
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$A-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\.(?:constructor|prototype))/,
        lookbehind: !0
      }
    ],
    keyword: [
      {
        pattern: /((?:^|\})\s*)catch\b/,
        lookbehind: !0
      },
      {
        pattern: /(^|[^.]|\.\.\.\s*)\b(?:as|assert(?=\s*\{)|async(?=\s*(?:function\b|\(|[$\w\xA0-\uFFFF]|$))|await|break|case|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally(?=\s*(?:\{|$))|for|from(?=\s*(?:['"]|$))|function|(?:get|set)(?=\s*(?:[#\[$\w\xA0-\uFFFF]|$))|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\b/,
        lookbehind: !0
      }
    ],
    // Allow for all non-ASCII characters (See http://stackoverflow.com/a/2008444)
    function: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,
    number: {
      pattern: RegExp(
        /(^|[^\w$])/.source + "(?:" + // constant
        (/NaN|Infinity/.source + "|" + // binary integer
        /0[bB][01]+(?:_[01]+)*n?/.source + "|" + // octal integer
        /0[oO][0-7]+(?:_[0-7]+)*n?/.source + "|" + // hexadecimal integer
        /0[xX][\dA-Fa-f]+(?:_[\dA-Fa-f]+)*n?/.source + "|" + // decimal bigint
        /\d+(?:_\d+)*n/.source + "|" + // decimal number (integer or float) but no bigint
        /(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[Ee][+-]?\d+(?:_\d+)*)?/.source) + ")" + /(?![\w$])/.source
      ),
      lookbehind: !0
    },
    operator: /--|\+\+|\*\*=?|=>|&&=?|\|\|=?|[!=]==|<<=?|>>>?=?|[-+*/%&|^!=<>]=?|\.{3}|\?\?=?|\?\.?|[~:]/
  }), e.languages.javascript["class-name"][0].pattern = /(\b(?:class|extends|implements|instanceof|interface|new)\s+)[\w.\\]+/, e.languages.insertBefore("javascript", "keyword", {
    regex: {
      pattern: RegExp(
        // lookbehind
        // eslint-disable-next-line regexp/no-dupe-characters-character-class
        /((?:^|[^$\w\xA0-\uFFFF."'\])\s]|\b(?:return|yield))\s*)/.source + // Regex pattern:
        // There are 2 regex patterns here. The RegExp set notation proposal added support for nested character
        // classes if the `v` flag is present. Unfortunately, nested CCs are both context-free and incompatible
        // with the only syntax, so we have to define 2 different regex patterns.
        /\//.source + "(?:" + /(?:\[(?:[^\]\\\r\n]|\\.)*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}/.source + "|" + // `v` flag syntax. This supports 3 levels of nested character classes.
        /(?:\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.)*\])*\])*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}v[dgimyus]{0,7}/.source + ")" + // lookahead
        /(?=(?:\s|\/\*(?:[^*]|\*(?!\/))*\*\/)*(?:$|[\r\n,.;:})\]]|\/\/))/.source
      ),
      lookbehind: !0,
      greedy: !0,
      inside: {
        "regex-source": {
          pattern: /^(\/)[\s\S]+(?=\/[a-z]*$)/,
          lookbehind: !0,
          alias: "language-regex",
          inside: e.languages.regex
        },
        "regex-delimiter": /^\/|\/$/,
        "regex-flags": /^[a-z]+$/
      }
    },
    // This must be declared before keyword because we use "function" inside the look-forward
    "function-variable": {
      pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^()]*\))*\)|(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/,
      alias: "function"
    },
    parameter: [
      {
        pattern: /(function(?:\s+(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,
        lookbehind: !0,
        inside: e.languages.javascript
      },
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=>)/i,
        lookbehind: !0,
        inside: e.languages.javascript
      },
      {
        pattern: /(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,
        lookbehind: !0,
        inside: e.languages.javascript
      },
      {
        pattern: /((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)(?![$\w\xA0-\uFFFF]))(?:(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/,
        lookbehind: !0,
        inside: e.languages.javascript
      }
    ],
    constant: /\b[A-Z](?:[A-Z_]|\dx?)*\b/
  }), e.languages.insertBefore("javascript", "string", {
    hashbang: {
      pattern: /^#!.*/,
      greedy: !0,
      alias: "comment"
    },
    "template-string": {
      pattern: /`(?:\\[\s\S]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}|(?!\$\{)[^\\`])*`/,
      greedy: !0,
      inside: {
        "template-punctuation": {
          pattern: /^`|`$/,
          alias: "string"
        },
        interpolation: {
          pattern: /((?:^|[^\\])(?:\\{2})*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}/,
          lookbehind: !0,
          inside: {
            "interpolation-punctuation": {
              pattern: /^\$\{|\}$/,
              alias: "punctuation"
            },
            rest: e.languages.javascript
          }
        },
        string: /[\s\S]+/
      }
    },
    "string-property": {
      pattern: /((?:^|[,{])[ \t]*)(["'])(?:\\(?:\r\n|[\s\S])|(?!\2)[^\\\r\n])*\2(?=\s*:)/m,
      lookbehind: !0,
      greedy: !0,
      alias: "property"
    }
  }), e.languages.insertBefore("javascript", "operator", {
    "literal-property": {
      pattern: /((?:^|[,{])[ \t]*)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*:)/m,
      lookbehind: !0,
      alias: "property"
    }
  }), e.languages.markup && (e.languages.markup.tag.addInlined("script", "javascript"), e.languages.markup.tag.addAttribute(
    /on(?:abort|blur|change|click|composition(?:end|start|update)|dblclick|error|focus(?:in|out)?|key(?:down|up)|load|mouse(?:down|enter|leave|move|out|over|up)|reset|resize|scroll|select|slotchange|submit|unload|wheel)/.source,
    "javascript"
  )), e.languages.js = e.languages.javascript, function() {
    if (typeof e > "u" || typeof document > "u")
      return;
    Element.prototype.matches || (Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector);
    var n = "Loading…", a = function(w, y) {
      return "✖ Error " + w + " while fetching file: " + y;
    }, o = "✖ Error: File does not exist or is empty", i = {
      js: "javascript",
      py: "python",
      rb: "ruby",
      ps1: "powershell",
      psm1: "powershell",
      sh: "bash",
      bat: "batch",
      h: "c",
      tex: "latex"
    }, r = "data-src-status", l = "loading", m = "loaded", g = "failed", F = "pre[data-src]:not([" + r + '="' + m + '"]):not([' + r + '="' + l + '"])';
    function u(w, y, x) {
      var d = new XMLHttpRequest();
      d.open("GET", w, !0), d.onreadystatechange = function() {
        d.readyState == 4 && (d.status < 400 && d.responseText ? y(d.responseText) : d.status >= 400 ? x(a(d.status, d.statusText)) : x(o));
      }, d.send(null);
    }
    function $(w) {
      var y = /^\s*(\d+)\s*(?:(,)\s*(?:(\d+)\s*)?)?$/.exec(w || "");
      if (y) {
        var x = Number(y[1]), d = y[2], c = y[3];
        return d ? c ? [x, Number(c)] : [x, void 0] : [x, x];
      }
    }
    e.hooks.add("before-highlightall", function(w) {
      w.selector += ", " + F;
    }), e.hooks.add("before-sanity-check", function(w) {
      var y = (
        /** @type {HTMLPreElement} */
        w.element
      );
      if (y.matches(F)) {
        w.code = "", y.setAttribute(r, l);
        var x = y.appendChild(document.createElement("CODE"));
        x.textContent = n;
        var d = y.getAttribute("data-src"), c = w.language;
        if (c === "none") {
          var _ = (/\.(\w+)$/.exec(d) || [, "none"])[1];
          c = i[_] || _;
        }
        e.util.setLanguage(x, c), e.util.setLanguage(y, c);
        var p = e.plugins.autoloader;
        p && p.loadLanguages(c), u(
          d,
          function(h) {
            y.setAttribute(r, m);
            var D = $(y.getAttribute("data-range"));
            if (D) {
              var b = h.split(/\r\n?|\n/g), v = D[0], C = D[1] == null ? b.length : D[1];
              v < 0 && (v += b.length), v = Math.max(0, Math.min(v - 1, b.length)), C < 0 && (C += b.length), C = Math.max(0, Math.min(C, b.length)), h = b.slice(v, C).join(`
`), y.hasAttribute("data-start") || y.setAttribute("data-start", String(v + 1));
            }
            x.textContent = h, e.highlightElement(x);
          },
          function(h) {
            y.setAttribute(r, g), x.textContent = h;
          }
        );
      }
    }), e.plugins.fileHighlight = {
      /**
       * Executes the File Highlight plugin for all matching `pre` elements under the given container.
       *
       * Note: Elements which are already loaded or currently loading will not be touched by this method.
       *
       * @param {ParentNode} [container=document]
       */
      highlight: function(y) {
        for (var x = (y || document).querySelectorAll(F), d = 0, c; c = x[d++]; )
          e.highlightElement(c);
      }
    };
    var B = !1;
    e.fileHighlight = function() {
      B || (console.warn("Prism.fileHighlight is deprecated. Use `Prism.plugins.fileHighlight.highlight` instead."), B = !0), e.plugins.fileHighlight.highlight.apply(this, arguments);
    };
  }();
})(fn);
Prism.languages.python = {
  comment: {
    pattern: /(^|[^\\])#.*/,
    lookbehind: !0,
    greedy: !0
  },
  "string-interpolation": {
    pattern: /(?:f|fr|rf)(?:("""|''')[\s\S]*?\1|("|')(?:\\.|(?!\2)[^\\\r\n])*\2)/i,
    greedy: !0,
    inside: {
      interpolation: {
        // "{" <expression> <optional "!s", "!r", or "!a"> <optional ":" format specifier> "}"
        pattern: /((?:^|[^{])(?:\{\{)*)\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}])+\})+\})+\}/,
        lookbehind: !0,
        inside: {
          "format-spec": {
            pattern: /(:)[^:(){}]+(?=\}$)/,
            lookbehind: !0
          },
          "conversion-option": {
            pattern: /![sra](?=[:}]$)/,
            alias: "punctuation"
          },
          rest: null
        }
      },
      string: /[\s\S]+/
    }
  },
  "triple-quoted-string": {
    pattern: /(?:[rub]|br|rb)?("""|''')[\s\S]*?\1/i,
    greedy: !0,
    alias: "string"
  },
  string: {
    pattern: /(?:[rub]|br|rb)?("|')(?:\\.|(?!\1)[^\\\r\n])*\1/i,
    greedy: !0
  },
  function: {
    pattern: /((?:^|\s)def[ \t]+)[a-zA-Z_]\w*(?=\s*\()/g,
    lookbehind: !0
  },
  "class-name": {
    pattern: /(\bclass\s+)\w+/i,
    lookbehind: !0
  },
  decorator: {
    pattern: /(^[\t ]*)@\w+(?:\.\w+)*/m,
    lookbehind: !0,
    alias: ["annotation", "punctuation"],
    inside: {
      punctuation: /\./
    }
  },
  keyword: /\b(?:_(?=\s*:)|and|as|assert|async|await|break|case|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|match|nonlocal|not|or|pass|print|raise|return|try|while|with|yield)\b/,
  builtin: /\b(?:__import__|abs|all|any|apply|ascii|basestring|bin|bool|buffer|bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|divmod|enumerate|eval|execfile|file|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|intern|isinstance|issubclass|iter|len|list|locals|long|map|max|memoryview|min|next|object|oct|open|ord|pow|property|range|raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|vars|xrange|zip)\b/,
  boolean: /\b(?:False|None|True)\b/,
  number: /\b0(?:b(?:_?[01])+|o(?:_?[0-7])+|x(?:_?[a-f0-9])+)\b|(?:\b\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\B\.\d+(?:_\d+)*)(?:e[+-]?\d+(?:_\d+)*)?j?(?!\w)/i,
  operator: /[-+%=]=?|!=|:=|\*\*?=?|\/\/?=?|<[<=>]?|>[=>]?|[&|^~]/,
  punctuation: /[{}[\];(),.:]/
};
Prism.languages.python["string-interpolation"].inside.interpolation.inside.rest = Prism.languages.python;
Prism.languages.py = Prism.languages.python;
(function(s) {
  var t = /\\(?:[^a-z()[\]]|[a-z*]+)/i, e = {
    "equation-command": {
      pattern: t,
      alias: "regex"
    }
  };
  s.languages.latex = {
    comment: /%.*/,
    // the verbatim environment prints whitespace to the document
    cdata: {
      pattern: /(\\begin\{((?:lstlisting|verbatim)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
      lookbehind: !0
    },
    /*
     * equations can be between $$ $$ or $ $ or \( \) or \[ \]
     * (all are multiline)
     */
    equation: [
      {
        pattern: /\$\$(?:\\[\s\S]|[^\\$])+\$\$|\$(?:\\[\s\S]|[^\\$])+\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]/,
        inside: e,
        alias: "string"
      },
      {
        pattern: /(\\begin\{((?:align|eqnarray|equation|gather|math|multline)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
        lookbehind: !0,
        inside: e,
        alias: "string"
      }
    ],
    /*
     * arguments which are keywords or references are highlighted
     * as keywords
     */
    keyword: {
      pattern: /(\\(?:begin|cite|documentclass|end|label|ref|usepackage)(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    url: {
      pattern: /(\\url\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    /*
     * section or chapter headlines are highlighted as bold so that
     * they stand out more
     */
    headline: {
      pattern: /(\\(?:chapter|frametitle|paragraph|part|section|subparagraph|subsection|subsubparagraph|subsubsection|subsubsubparagraph)\*?(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0,
      alias: "class-name"
    },
    function: {
      pattern: t,
      alias: "selector"
    },
    punctuation: /[[\]{}&]/
  }, s.languages.tex = s.languages.latex, s.languages.context = s.languages.latex;
})(Prism);
(function(s) {
  var t = "\\b(?:BASH|BASHOPTS|BASH_ALIASES|BASH_ARGC|BASH_ARGV|BASH_CMDS|BASH_COMPLETION_COMPAT_DIR|BASH_LINENO|BASH_REMATCH|BASH_SOURCE|BASH_VERSINFO|BASH_VERSION|COLORTERM|COLUMNS|COMP_WORDBREAKS|DBUS_SESSION_BUS_ADDRESS|DEFAULTS_PATH|DESKTOP_SESSION|DIRSTACK|DISPLAY|EUID|GDMSESSION|GDM_LANG|GNOME_KEYRING_CONTROL|GNOME_KEYRING_PID|GPG_AGENT_INFO|GROUPS|HISTCONTROL|HISTFILE|HISTFILESIZE|HISTSIZE|HOME|HOSTNAME|HOSTTYPE|IFS|INSTANCE|JOB|LANG|LANGUAGE|LC_ADDRESS|LC_ALL|LC_IDENTIFICATION|LC_MEASUREMENT|LC_MONETARY|LC_NAME|LC_NUMERIC|LC_PAPER|LC_TELEPHONE|LC_TIME|LESSCLOSE|LESSOPEN|LINES|LOGNAME|LS_COLORS|MACHTYPE|MAILCHECK|MANDATORY_PATH|NO_AT_BRIDGE|OLDPWD|OPTERR|OPTIND|ORBIT_SOCKETDIR|OSTYPE|PAPERSIZE|PATH|PIPESTATUS|PPID|PS1|PS2|PS3|PS4|PWD|RANDOM|REPLY|SECONDS|SELINUX_INIT|SESSION|SESSIONTYPE|SESSION_MANAGER|SHELL|SHELLOPTS|SHLVL|SSH_AUTH_SOCK|TERM|UID|UPSTART_EVENTS|UPSTART_INSTANCE|UPSTART_JOB|UPSTART_SESSION|USER|WINDOWID|XAUTHORITY|XDG_CONFIG_DIRS|XDG_CURRENT_DESKTOP|XDG_DATA_DIRS|XDG_GREETER_DATA_DIR|XDG_MENU_PREFIX|XDG_RUNTIME_DIR|XDG_SEAT|XDG_SEAT_PATH|XDG_SESSION_DESKTOP|XDG_SESSION_ID|XDG_SESSION_PATH|XDG_SESSION_TYPE|XDG_VTNR|XMODIFIERS)\\b", e = {
    pattern: /(^(["']?)\w+\2)[ \t]+\S.*/,
    lookbehind: !0,
    alias: "punctuation",
    // this looks reasonably well in all themes
    inside: null
    // see below
  }, n = {
    bash: e,
    environment: {
      pattern: RegExp("\\$" + t),
      alias: "constant"
    },
    variable: [
      // [0]: Arithmetic Environment
      {
        pattern: /\$?\(\([\s\S]+?\)\)/,
        greedy: !0,
        inside: {
          // If there is a $ sign at the beginning highlight $(( and )) as variable
          variable: [
            {
              pattern: /(^\$\(\([\s\S]+)\)\)/,
              lookbehind: !0
            },
            /^\$\(\(/
          ],
          number: /\b0x[\dA-Fa-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:[Ee]-?\d+)?/,
          // Operators according to https://www.gnu.org/software/bash/manual/bashref.html#Shell-Arithmetic
          operator: /--|\+\+|\*\*=?|<<=?|>>=?|&&|\|\||[=!+\-*/%<>^&|]=?|[?~:]/,
          // If there is no $ sign at the beginning highlight (( and )) as punctuation
          punctuation: /\(\(?|\)\)?|,|;/
        }
      },
      // [1]: Command Substitution
      {
        pattern: /\$\((?:\([^)]+\)|[^()])+\)|`[^`]+`/,
        greedy: !0,
        inside: {
          variable: /^\$\(|^`|\)$|`$/
        }
      },
      // [2]: Brace expansion
      {
        pattern: /\$\{[^}]+\}/,
        greedy: !0,
        inside: {
          operator: /:[-=?+]?|[!\/]|##?|%%?|\^\^?|,,?/,
          punctuation: /[\[\]]/,
          environment: {
            pattern: RegExp("(\\{)" + t),
            lookbehind: !0,
            alias: "constant"
          }
        }
      },
      /\$(?:\w+|[#?*!@$])/
    ],
    // Escape sequences from echo and printf's manuals, and escaped quotes.
    entity: /\\(?:[abceEfnrtv\\"]|O?[0-7]{1,3}|U[0-9a-fA-F]{8}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{1,2})/
  };
  s.languages.bash = {
    shebang: {
      pattern: /^#!\s*\/.*/,
      alias: "important"
    },
    comment: {
      pattern: /(^|[^"{\\$])#.*/,
      lookbehind: !0
    },
    "function-name": [
      // a) function foo {
      // b) foo() {
      // c) function foo() {
      // but not “foo {”
      {
        // a) and c)
        pattern: /(\bfunction\s+)[\w-]+(?=(?:\s*\(?:\s*\))?\s*\{)/,
        lookbehind: !0,
        alias: "function"
      },
      {
        // b)
        pattern: /\b[\w-]+(?=\s*\(\s*\)\s*\{)/,
        alias: "function"
      }
    ],
    // Highlight variable names as variables in for and select beginnings.
    "for-or-select": {
      pattern: /(\b(?:for|select)\s+)\w+(?=\s+in\s)/,
      alias: "variable",
      lookbehind: !0
    },
    // Highlight variable names as variables in the left-hand part
    // of assignments (“=” and “+=”).
    "assign-left": {
      pattern: /(^|[\s;|&]|[<>]\()\w+(?:\.\w+)*(?=\+?=)/,
      inside: {
        environment: {
          pattern: RegExp("(^|[\\s;|&]|[<>]\\()" + t),
          lookbehind: !0,
          alias: "constant"
        }
      },
      alias: "variable",
      lookbehind: !0
    },
    // Highlight parameter names as variables
    parameter: {
      pattern: /(^|\s)-{1,2}(?:\w+:[+-]?)?\w+(?:\.\w+)*(?=[=\s]|$)/,
      alias: "variable",
      lookbehind: !0
    },
    string: [
      // Support for Here-documents https://en.wikipedia.org/wiki/Here_document
      {
        pattern: /((?:^|[^<])<<-?\s*)(\w+)\s[\s\S]*?(?:\r?\n|\r)\2/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      // Here-document with quotes around the tag
      // → No expansion (so no “inside”).
      {
        pattern: /((?:^|[^<])<<-?\s*)(["'])(\w+)\2\s[\s\S]*?(?:\r?\n|\r)\3/,
        lookbehind: !0,
        greedy: !0,
        inside: {
          bash: e
        }
      },
      // “Normal” string
      {
        // https://www.gnu.org/software/bash/manual/html_node/Double-Quotes.html
        pattern: /(^|[^\\](?:\\\\)*)"(?:\\[\s\S]|\$\([^)]+\)|\$(?!\()|`[^`]+`|[^"\\`$])*"/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/Single-Quotes.html
        pattern: /(^|[^$\\])'[^']*'/,
        lookbehind: !0,
        greedy: !0
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html
        pattern: /\$'(?:[^'\\]|\\[\s\S])*'/,
        greedy: !0,
        inside: {
          entity: n.entity
        }
      }
    ],
    environment: {
      pattern: RegExp("\\$?" + t),
      alias: "constant"
    },
    variable: n.variable,
    function: {
      pattern: /(^|[\s;|&]|[<>]\()(?:add|apropos|apt|apt-cache|apt-get|aptitude|aspell|automysqlbackup|awk|basename|bash|bc|bconsole|bg|bzip2|cal|cargo|cat|cfdisk|chgrp|chkconfig|chmod|chown|chroot|cksum|clear|cmp|column|comm|composer|cp|cron|crontab|csplit|curl|cut|date|dc|dd|ddrescue|debootstrap|df|diff|diff3|dig|dir|dircolors|dirname|dirs|dmesg|docker|docker-compose|du|egrep|eject|env|ethtool|expand|expect|expr|fdformat|fdisk|fg|fgrep|file|find|fmt|fold|format|free|fsck|ftp|fuser|gawk|git|gparted|grep|groupadd|groupdel|groupmod|groups|grub-mkconfig|gzip|halt|head|hg|history|host|hostname|htop|iconv|id|ifconfig|ifdown|ifup|import|install|ip|java|jobs|join|kill|killall|less|link|ln|locate|logname|logrotate|look|lpc|lpr|lprint|lprintd|lprintq|lprm|ls|lsof|lynx|make|man|mc|mdadm|mkconfig|mkdir|mke2fs|mkfifo|mkfs|mkisofs|mknod|mkswap|mmv|more|most|mount|mtools|mtr|mutt|mv|nano|nc|netstat|nice|nl|node|nohup|notify-send|npm|nslookup|op|open|parted|passwd|paste|pathchk|ping|pkill|pnpm|podman|podman-compose|popd|pr|printcap|printenv|ps|pushd|pv|quota|quotacheck|quotactl|ram|rar|rcp|reboot|remsync|rename|renice|rev|rm|rmdir|rpm|rsync|scp|screen|sdiff|sed|sendmail|seq|service|sftp|sh|shellcheck|shuf|shutdown|sleep|slocate|sort|split|ssh|stat|strace|su|sudo|sum|suspend|swapon|sync|sysctl|tac|tail|tar|tee|time|timeout|top|touch|tr|traceroute|tsort|tty|umount|uname|unexpand|uniq|units|unrar|unshar|unzip|update-grub|uptime|useradd|userdel|usermod|users|uudecode|uuencode|v|vcpkg|vdir|vi|vim|virsh|vmstat|wait|watch|wc|wget|whereis|which|who|whoami|write|xargs|xdg-open|yarn|yes|zenity|zip|zsh|zypper)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    keyword: {
      pattern: /(^|[\s;|&]|[<>]\()(?:case|do|done|elif|else|esac|fi|for|function|if|in|select|then|until|while)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    // https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html
    builtin: {
      pattern: /(^|[\s;|&]|[<>]\()(?:\.|:|alias|bind|break|builtin|caller|cd|command|continue|declare|echo|enable|eval|exec|exit|export|getopts|hash|help|let|local|logout|mapfile|printf|pwd|read|readarray|readonly|return|set|shift|shopt|source|test|times|trap|type|typeset|ulimit|umask|unalias|unset)(?=$|[)\s;|&])/,
      lookbehind: !0,
      // Alias added to make those easier to distinguish from strings.
      alias: "class-name"
    },
    boolean: {
      pattern: /(^|[\s;|&]|[<>]\()(?:false|true)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    "file-descriptor": {
      pattern: /\B&\d\b/,
      alias: "important"
    },
    operator: {
      // Lots of redirections here, but not just that.
      pattern: /\d?<>|>\||\+=|=[=~]?|!=?|<<[<-]?|[&\d]?>>|\d[<>]&?|[<>][&=]?|&[>&]?|\|[&|]?/,
      inside: {
        "file-descriptor": {
          pattern: /^\d/,
          alias: "important"
        }
      }
    },
    punctuation: /\$?\(\(?|\)\)?|\.\.|[{}[\];\\]/,
    number: {
      pattern: /(^|\s)(?:[1-9]\d*|0)(?:[.,]\d+)?\b/,
      lookbehind: !0
    }
  }, e.inside = s.languages.bash;
  for (var a = [
    "comment",
    "function-name",
    "for-or-select",
    "assign-left",
    "parameter",
    "string",
    "environment",
    "function",
    "keyword",
    "builtin",
    "boolean",
    "file-descriptor",
    "operator",
    "punctuation",
    "number"
  ], o = n.variable[1].inside, i = 0; i < a.length; i++)
    o[a[i]] = s.languages.bash[a[i]];
  s.languages.sh = s.languages.bash, s.languages.shell = s.languages.bash;
})(Prism);
new dt();
const $n = (s) => {
  const t = {};
  for (let e = 0, n = s.length; e < n; e++) {
    const a = s[e];
    for (const o in a)
      t[o] ? t[o] = t[o].concat(a[o]) : t[o] = a[o];
  }
  return t;
}, Dn = [
  "abbr",
  "accept",
  "accept-charset",
  "accesskey",
  "action",
  "align",
  "alink",
  "allow",
  "allowfullscreen",
  "alt",
  "anchor",
  "archive",
  "as",
  "async",
  "autocapitalize",
  "autocomplete",
  "autocorrect",
  "autofocus",
  "autopictureinpicture",
  "autoplay",
  "axis",
  "background",
  "behavior",
  "bgcolor",
  "border",
  "bordercolor",
  "capture",
  "cellpadding",
  "cellspacing",
  "challenge",
  "char",
  "charoff",
  "charset",
  "checked",
  "cite",
  "class",
  "classid",
  "clear",
  "code",
  "codebase",
  "codetype",
  "color",
  "cols",
  "colspan",
  "compact",
  "content",
  "contenteditable",
  "controls",
  "controlslist",
  "conversiondestination",
  "coords",
  "crossorigin",
  "csp",
  "data",
  "datetime",
  "declare",
  "decoding",
  "default",
  "defer",
  "dir",
  "direction",
  "dirname",
  "disabled",
  "disablepictureinpicture",
  "disableremoteplayback",
  "disallowdocumentaccess",
  "download",
  "draggable",
  "elementtiming",
  "enctype",
  "end",
  "enterkeyhint",
  "event",
  "exportparts",
  "face",
  "for",
  "form",
  "formaction",
  "formenctype",
  "formmethod",
  "formnovalidate",
  "formtarget",
  "frame",
  "frameborder",
  "headers",
  "height",
  "hidden",
  "high",
  "href",
  "hreflang",
  "hreftranslate",
  "hspace",
  "http-equiv",
  "id",
  "imagesizes",
  "imagesrcset",
  "importance",
  "impressiondata",
  "impressionexpiry",
  "incremental",
  "inert",
  "inputmode",
  "integrity",
  "invisible",
  "ismap",
  "keytype",
  "kind",
  "label",
  "lang",
  "language",
  "latencyhint",
  "leftmargin",
  "link",
  "list",
  "loading",
  "longdesc",
  "loop",
  "low",
  "lowsrc",
  "manifest",
  "marginheight",
  "marginwidth",
  "max",
  "maxlength",
  "mayscript",
  "media",
  "method",
  "min",
  "minlength",
  "multiple",
  "muted",
  "name",
  "nohref",
  "nomodule",
  "nonce",
  "noresize",
  "noshade",
  "novalidate",
  "nowrap",
  "object",
  "open",
  "optimum",
  "part",
  "pattern",
  "ping",
  "placeholder",
  "playsinline",
  "policy",
  "poster",
  "preload",
  "pseudo",
  "readonly",
  "referrerpolicy",
  "rel",
  "reportingorigin",
  "required",
  "resources",
  "rev",
  "reversed",
  "role",
  "rows",
  "rowspan",
  "rules",
  "sandbox",
  "scheme",
  "scope",
  "scopes",
  "scrollamount",
  "scrolldelay",
  "scrolling",
  "select",
  "selected",
  "shadowroot",
  "shadowrootdelegatesfocus",
  "shape",
  "size",
  "sizes",
  "slot",
  "span",
  "spellcheck",
  "src",
  "srclang",
  "srcset",
  "standby",
  "start",
  "step",
  "style",
  "summary",
  "tabindex",
  "target",
  "text",
  "title",
  "topmargin",
  "translate",
  "truespeed",
  "trusttoken",
  "type",
  "usemap",
  "valign",
  "value",
  "valuetype",
  "version",
  "virtualkeyboardpolicy",
  "vlink",
  "vspace",
  "webkitdirectory",
  "width",
  "wrap"
], vn = [
  "accent-height",
  "accumulate",
  "additive",
  "alignment-baseline",
  "ascent",
  "attributename",
  "attributetype",
  "azimuth",
  "basefrequency",
  "baseline-shift",
  "begin",
  "bias",
  "by",
  "class",
  "clip",
  "clippathunits",
  "clip-path",
  "clip-rule",
  "color",
  "color-interpolation",
  "color-interpolation-filters",
  "color-profile",
  "color-rendering",
  "cx",
  "cy",
  "d",
  "dx",
  "dy",
  "diffuseconstant",
  "direction",
  "display",
  "divisor",
  "dominant-baseline",
  "dur",
  "edgemode",
  "elevation",
  "end",
  "fill",
  "fill-opacity",
  "fill-rule",
  "filter",
  "filterunits",
  "flood-color",
  "flood-opacity",
  "font-family",
  "font-size",
  "font-size-adjust",
  "font-stretch",
  "font-style",
  "font-variant",
  "font-weight",
  "fx",
  "fy",
  "g1",
  "g2",
  "glyph-name",
  "glyphref",
  "gradientunits",
  "gradienttransform",
  "height",
  "href",
  "id",
  "image-rendering",
  "in",
  "in2",
  "k",
  "k1",
  "k2",
  "k3",
  "k4",
  "kerning",
  "keypoints",
  "keysplines",
  "keytimes",
  "lang",
  "lengthadjust",
  "letter-spacing",
  "kernelmatrix",
  "kernelunitlength",
  "lighting-color",
  "local",
  "marker-end",
  "marker-mid",
  "marker-start",
  "markerheight",
  "markerunits",
  "markerwidth",
  "maskcontentunits",
  "maskunits",
  "max",
  "mask",
  "media",
  "method",
  "mode",
  "min",
  "name",
  "numoctaves",
  "offset",
  "operator",
  "opacity",
  "order",
  "orient",
  "orientation",
  "origin",
  "overflow",
  "paint-order",
  "path",
  "pathlength",
  "patterncontentunits",
  "patterntransform",
  "patternunits",
  "points",
  "preservealpha",
  "preserveaspectratio",
  "primitiveunits",
  "r",
  "rx",
  "ry",
  "radius",
  "refx",
  "refy",
  "repeatcount",
  "repeatdur",
  "restart",
  "result",
  "rotate",
  "scale",
  "seed",
  "shape-rendering",
  "specularconstant",
  "specularexponent",
  "spreadmethod",
  "startoffset",
  "stddeviation",
  "stitchtiles",
  "stop-color",
  "stop-opacity",
  "stroke-dasharray",
  "stroke-dashoffset",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-miterlimit",
  "stroke-opacity",
  "stroke",
  "stroke-width",
  "style",
  "surfacescale",
  "systemlanguage",
  "tabindex",
  "targetx",
  "targety",
  "transform",
  "transform-origin",
  "text-anchor",
  "text-decoration",
  "text-rendering",
  "textlength",
  "type",
  "u1",
  "u2",
  "unicode",
  "values",
  "viewbox",
  "visibility",
  "version",
  "vert-adv-y",
  "vert-origin-x",
  "vert-origin-y",
  "width",
  "word-spacing",
  "wrap",
  "writing-mode",
  "xchannelselector",
  "ychannelselector",
  "x",
  "x1",
  "x2",
  "xmlns",
  "y",
  "y1",
  "y2",
  "z",
  "zoomandpan"
], Fn = [
  "accent",
  "accentunder",
  "align",
  "bevelled",
  "close",
  "columnsalign",
  "columnlines",
  "columnspan",
  "denomalign",
  "depth",
  "dir",
  "display",
  "displaystyle",
  "encoding",
  "fence",
  "frame",
  "height",
  "href",
  "id",
  "largeop",
  "length",
  "linethickness",
  "lspace",
  "lquote",
  "mathbackground",
  "mathcolor",
  "mathsize",
  "mathvariant",
  "maxsize",
  "minsize",
  "movablelimits",
  "notation",
  "numalign",
  "open",
  "rowalign",
  "rowlines",
  "rowspacing",
  "rowspan",
  "rspace",
  "rquote",
  "scriptlevel",
  "scriptminsize",
  "scriptsizemultiplier",
  "selection",
  "separator",
  "separators",
  "stretchy",
  "subscriptshift",
  "supscriptshift",
  "symmetric",
  "voffset",
  "width",
  "xmlns"
];
$n([
  Object.fromEntries(Dn.map((s) => [s, ["*"]])),
  Object.fromEntries(vn.map((s) => [s, ["svg:*"]])),
  Object.fromEntries(Fn.map((s) => [s, ["math:*"]]))
]);
const {
  HtmlTagHydration: Hn,
  SvelteComponent: jn,
  attr: Gn,
  binding_callbacks: Un,
  children: Zn,
  claim_element: Xn,
  claim_html_tag: Yn,
  detach: Wn,
  element: Qn,
  init: Kn,
  insert_hydration: Vn,
  noop: Jn,
  safe_not_equal: ei,
  toggle_class: ti
} = window.__gradio__svelte__internal, { afterUpdate: ni, tick: ii, onMount: ai } = window.__gradio__svelte__internal, {
  SvelteComponent: oi,
  attr: ri,
  children: si,
  claim_component: li,
  claim_element: ui,
  create_component: ci,
  destroy_component: di,
  detach: _i,
  element: pi,
  init: hi,
  insert_hydration: mi,
  mount_component: gi,
  safe_not_equal: fi,
  transition_in: $i,
  transition_out: Di
} = window.__gradio__svelte__internal, {
  SvelteComponent: vi,
  attr: Fi,
  check_outros: yi,
  children: bi,
  claim_component: wi,
  claim_element: Ci,
  claim_space: ki,
  create_component: Ei,
  create_slot: Ai,
  destroy_component: xi,
  detach: Si,
  element: Bi,
  empty: qi,
  get_all_dirty_from_scope: Ti,
  get_slot_changes: Ii,
  group_outros: Ri,
  init: zi,
  insert_hydration: Li,
  mount_component: Oi,
  safe_not_equal: Pi,
  space: Mi,
  toggle_class: Ni,
  transition_in: Hi,
  transition_out: ji,
  update_slot_base: Gi
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ui,
  append_hydration: Zi,
  attr: Xi,
  children: Yi,
  claim_component: Wi,
  claim_element: Qi,
  claim_space: Ki,
  claim_text: Vi,
  create_component: Ji,
  destroy_component: ea,
  detach: ta,
  element: na,
  init: ia,
  insert_hydration: aa,
  mount_component: oa,
  safe_not_equal: ra,
  set_data: sa,
  space: la,
  text: ua,
  toggle_class: ca,
  transition_in: da,
  transition_out: _a
} = window.__gradio__svelte__internal, {
  SvelteComponent: pa,
  append_hydration: ha,
  attr: ma,
  bubble: ga,
  check_outros: fa,
  children: $a,
  claim_component: Da,
  claim_element: va,
  claim_space: Fa,
  claim_text: ya,
  construct_svelte_component: ba,
  create_component: wa,
  create_slot: Ca,
  destroy_component: ka,
  detach: Ea,
  element: Aa,
  get_all_dirty_from_scope: xa,
  get_slot_changes: Sa,
  group_outros: Ba,
  init: qa,
  insert_hydration: Ta,
  listen: Ia,
  mount_component: Ra,
  safe_not_equal: za,
  set_data: La,
  set_style: Oa,
  space: Pa,
  text: Ma,
  toggle_class: Na,
  transition_in: Ha,
  transition_out: ja,
  update_slot_base: Ga
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ua,
  append_hydration: Za,
  attr: Xa,
  binding_callbacks: Ya,
  children: Wa,
  claim_element: Qa,
  create_slot: Ka,
  detach: Va,
  element: Ja,
  get_all_dirty_from_scope: eo,
  get_slot_changes: to,
  init: no,
  insert_hydration: io,
  safe_not_equal: ao,
  toggle_class: oo,
  transition_in: ro,
  transition_out: so,
  update_slot_base: lo
} = window.__gradio__svelte__internal, {
  SvelteComponent: uo,
  append_hydration: co,
  attr: _o,
  children: po,
  claim_svg_element: ho,
  detach: mo,
  init: go,
  insert_hydration: fo,
  noop: $o,
  safe_not_equal: Do,
  svg_element: vo
} = window.__gradio__svelte__internal, {
  SvelteComponent: Fo,
  append_hydration: yo,
  attr: bo,
  children: wo,
  claim_svg_element: Co,
  detach: ko,
  init: Eo,
  insert_hydration: Ao,
  noop: xo,
  safe_not_equal: So,
  svg_element: Bo
} = window.__gradio__svelte__internal, {
  SvelteComponent: qo,
  append_hydration: To,
  attr: Io,
  children: Ro,
  claim_svg_element: zo,
  detach: Lo,
  init: Oo,
  insert_hydration: Po,
  noop: Mo,
  safe_not_equal: No,
  svg_element: Ho
} = window.__gradio__svelte__internal, {
  SvelteComponent: jo,
  append_hydration: Go,
  attr: Uo,
  children: Zo,
  claim_svg_element: Xo,
  detach: Yo,
  init: Wo,
  insert_hydration: Qo,
  noop: Ko,
  safe_not_equal: Vo,
  svg_element: Jo
} = window.__gradio__svelte__internal, {
  SvelteComponent: er,
  append_hydration: tr,
  attr: nr,
  children: ir,
  claim_svg_element: ar,
  detach: or,
  init: rr,
  insert_hydration: sr,
  noop: lr,
  safe_not_equal: ur,
  svg_element: cr
} = window.__gradio__svelte__internal, {
  SvelteComponent: dr,
  append_hydration: _r,
  attr: pr,
  children: hr,
  claim_svg_element: mr,
  detach: gr,
  init: fr,
  insert_hydration: $r,
  noop: Dr,
  safe_not_equal: vr,
  svg_element: Fr
} = window.__gradio__svelte__internal, {
  SvelteComponent: yr,
  append_hydration: br,
  attr: wr,
  children: Cr,
  claim_svg_element: kr,
  detach: Er,
  init: Ar,
  insert_hydration: xr,
  noop: Sr,
  safe_not_equal: Br,
  svg_element: qr
} = window.__gradio__svelte__internal, {
  SvelteComponent: Tr,
  append_hydration: Ir,
  attr: Rr,
  children: zr,
  claim_svg_element: Lr,
  detach: Or,
  init: Pr,
  insert_hydration: Mr,
  noop: Nr,
  safe_not_equal: Hr,
  svg_element: jr
} = window.__gradio__svelte__internal, {
  SvelteComponent: Gr,
  append_hydration: Ur,
  attr: Zr,
  children: Xr,
  claim_svg_element: Yr,
  detach: Wr,
  init: Qr,
  insert_hydration: Kr,
  noop: Vr,
  safe_not_equal: Jr,
  svg_element: es
} = window.__gradio__svelte__internal, {
  SvelteComponent: ts,
  append_hydration: ns,
  attr: is,
  children: as,
  claim_svg_element: os,
  detach: rs,
  init: ss,
  insert_hydration: ls,
  noop: us,
  safe_not_equal: cs,
  svg_element: ds
} = window.__gradio__svelte__internal, {
  SvelteComponent: _s,
  append_hydration: ps,
  attr: hs,
  children: ms,
  claim_svg_element: gs,
  detach: fs,
  init: $s,
  insert_hydration: Ds,
  noop: vs,
  safe_not_equal: Fs,
  svg_element: ys
} = window.__gradio__svelte__internal, {
  SvelteComponent: bs,
  append_hydration: ws,
  attr: Cs,
  children: ks,
  claim_svg_element: Es,
  detach: As,
  init: xs,
  insert_hydration: Ss,
  noop: Bs,
  safe_not_equal: qs,
  svg_element: Ts
} = window.__gradio__svelte__internal, {
  SvelteComponent: Is,
  append_hydration: Rs,
  attr: zs,
  children: Ls,
  claim_svg_element: Os,
  detach: Ps,
  init: Ms,
  insert_hydration: Ns,
  noop: Hs,
  safe_not_equal: js,
  set_style: Gs,
  svg_element: Us
} = window.__gradio__svelte__internal, {
  SvelteComponent: Zs,
  append_hydration: Xs,
  attr: Ys,
  children: Ws,
  claim_svg_element: Qs,
  detach: Ks,
  init: Vs,
  insert_hydration: Js,
  noop: el,
  safe_not_equal: tl,
  svg_element: nl
} = window.__gradio__svelte__internal, {
  SvelteComponent: il,
  append_hydration: al,
  attr: ol,
  children: rl,
  claim_svg_element: sl,
  detach: ll,
  init: ul,
  insert_hydration: cl,
  noop: dl,
  safe_not_equal: _l,
  svg_element: pl
} = window.__gradio__svelte__internal, {
  SvelteComponent: hl,
  append_hydration: ml,
  attr: gl,
  children: fl,
  claim_svg_element: $l,
  detach: Dl,
  init: vl,
  insert_hydration: Fl,
  noop: yl,
  safe_not_equal: bl,
  svg_element: wl
} = window.__gradio__svelte__internal, {
  SvelteComponent: Cl,
  append_hydration: kl,
  attr: El,
  children: Al,
  claim_svg_element: xl,
  detach: Sl,
  init: Bl,
  insert_hydration: ql,
  noop: Tl,
  safe_not_equal: Il,
  svg_element: Rl
} = window.__gradio__svelte__internal, {
  SvelteComponent: zl,
  append_hydration: Ll,
  attr: Ol,
  children: Pl,
  claim_svg_element: Ml,
  detach: Nl,
  init: Hl,
  insert_hydration: jl,
  noop: Gl,
  safe_not_equal: Ul,
  svg_element: Zl
} = window.__gradio__svelte__internal, {
  SvelteComponent: Xl,
  append_hydration: Yl,
  attr: Wl,
  children: Ql,
  claim_svg_element: Kl,
  detach: Vl,
  init: Jl,
  insert_hydration: eu,
  noop: tu,
  safe_not_equal: nu,
  svg_element: iu
} = window.__gradio__svelte__internal, {
  SvelteComponent: au,
  append_hydration: ou,
  attr: ru,
  children: su,
  claim_svg_element: lu,
  detach: uu,
  init: cu,
  insert_hydration: du,
  noop: _u,
  safe_not_equal: pu,
  svg_element: hu
} = window.__gradio__svelte__internal, {
  SvelteComponent: mu,
  append_hydration: gu,
  attr: fu,
  children: $u,
  claim_svg_element: Du,
  detach: vu,
  init: Fu,
  insert_hydration: yu,
  noop: bu,
  safe_not_equal: wu,
  svg_element: Cu
} = window.__gradio__svelte__internal, {
  SvelteComponent: ku,
  append_hydration: Eu,
  attr: Au,
  children: xu,
  claim_svg_element: Su,
  detach: Bu,
  init: qu,
  insert_hydration: Tu,
  noop: Iu,
  safe_not_equal: Ru,
  svg_element: zu
} = window.__gradio__svelte__internal, {
  SvelteComponent: Lu,
  append_hydration: Ou,
  attr: Pu,
  children: Mu,
  claim_svg_element: Nu,
  detach: Hu,
  init: ju,
  insert_hydration: Gu,
  noop: Uu,
  safe_not_equal: Zu,
  svg_element: Xu
} = window.__gradio__svelte__internal, {
  SvelteComponent: Yu,
  append_hydration: Wu,
  attr: Qu,
  children: Ku,
  claim_svg_element: Vu,
  detach: Ju,
  init: ec,
  insert_hydration: tc,
  noop: nc,
  safe_not_equal: ic,
  svg_element: ac
} = window.__gradio__svelte__internal, {
  SvelteComponent: oc,
  append_hydration: rc,
  attr: sc,
  children: lc,
  claim_svg_element: uc,
  detach: cc,
  init: dc,
  insert_hydration: _c,
  noop: pc,
  safe_not_equal: hc,
  svg_element: mc
} = window.__gradio__svelte__internal, {
  SvelteComponent: gc,
  append_hydration: fc,
  attr: $c,
  children: Dc,
  claim_svg_element: vc,
  detach: Fc,
  init: yc,
  insert_hydration: bc,
  noop: wc,
  safe_not_equal: Cc,
  svg_element: kc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ec,
  append_hydration: Ac,
  attr: xc,
  children: Sc,
  claim_svg_element: Bc,
  detach: qc,
  init: Tc,
  insert_hydration: Ic,
  noop: Rc,
  safe_not_equal: zc,
  svg_element: Lc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Oc,
  append_hydration: Pc,
  attr: Mc,
  children: Nc,
  claim_svg_element: Hc,
  detach: jc,
  init: Gc,
  insert_hydration: Uc,
  noop: Zc,
  safe_not_equal: Xc,
  svg_element: Yc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Wc,
  append_hydration: Qc,
  attr: Kc,
  children: Vc,
  claim_svg_element: Jc,
  detach: ed,
  init: td,
  insert_hydration: nd,
  noop: id,
  safe_not_equal: ad,
  svg_element: od
} = window.__gradio__svelte__internal, {
  SvelteComponent: rd,
  append_hydration: sd,
  attr: ld,
  children: ud,
  claim_svg_element: cd,
  detach: dd,
  init: _d,
  insert_hydration: pd,
  noop: hd,
  safe_not_equal: md,
  svg_element: gd
} = window.__gradio__svelte__internal, {
  SvelteComponent: fd,
  append_hydration: $d,
  attr: Dd,
  children: vd,
  claim_svg_element: Fd,
  detach: yd,
  init: bd,
  insert_hydration: wd,
  noop: Cd,
  safe_not_equal: kd,
  svg_element: Ed
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ad,
  append_hydration: xd,
  attr: Sd,
  children: Bd,
  claim_svg_element: qd,
  detach: Td,
  init: Id,
  insert_hydration: Rd,
  noop: zd,
  safe_not_equal: Ld,
  svg_element: Od
} = window.__gradio__svelte__internal, {
  SvelteComponent: Pd,
  append_hydration: Md,
  attr: Nd,
  children: Hd,
  claim_svg_element: jd,
  detach: Gd,
  init: Ud,
  insert_hydration: Zd,
  noop: Xd,
  safe_not_equal: Yd,
  svg_element: Wd
} = window.__gradio__svelte__internal, {
  SvelteComponent: Qd,
  append_hydration: Kd,
  attr: Vd,
  children: Jd,
  claim_svg_element: e_,
  detach: t_,
  init: n_,
  insert_hydration: i_,
  noop: a_,
  safe_not_equal: o_,
  svg_element: r_
} = window.__gradio__svelte__internal, {
  SvelteComponent: s_,
  append_hydration: l_,
  attr: u_,
  children: c_,
  claim_svg_element: d_,
  detach: __,
  init: p_,
  insert_hydration: h_,
  noop: m_,
  safe_not_equal: g_,
  svg_element: f_
} = window.__gradio__svelte__internal, {
  SvelteComponent: $_,
  append_hydration: D_,
  attr: v_,
  children: F_,
  claim_svg_element: y_,
  detach: b_,
  init: w_,
  insert_hydration: C_,
  noop: k_,
  safe_not_equal: E_,
  svg_element: A_
} = window.__gradio__svelte__internal, {
  SvelteComponent: x_,
  append_hydration: S_,
  attr: B_,
  children: q_,
  claim_svg_element: T_,
  detach: I_,
  init: R_,
  insert_hydration: z_,
  noop: L_,
  safe_not_equal: O_,
  svg_element: P_
} = window.__gradio__svelte__internal, {
  SvelteComponent: M_,
  append_hydration: N_,
  attr: H_,
  children: j_,
  claim_svg_element: G_,
  detach: U_,
  init: Z_,
  insert_hydration: X_,
  noop: Y_,
  safe_not_equal: W_,
  svg_element: Q_
} = window.__gradio__svelte__internal, {
  SvelteComponent: K_,
  append_hydration: V_,
  attr: J_,
  children: ep,
  claim_svg_element: tp,
  detach: np,
  init: ip,
  insert_hydration: ap,
  noop: op,
  safe_not_equal: rp,
  svg_element: sp
} = window.__gradio__svelte__internal, {
  SvelteComponent: lp,
  append_hydration: up,
  attr: cp,
  children: dp,
  claim_svg_element: _p,
  detach: pp,
  init: hp,
  insert_hydration: mp,
  noop: gp,
  safe_not_equal: fp,
  svg_element: $p
} = window.__gradio__svelte__internal, {
  SvelteComponent: Dp,
  append_hydration: vp,
  attr: Fp,
  children: yp,
  claim_svg_element: bp,
  detach: wp,
  init: Cp,
  insert_hydration: kp,
  noop: Ep,
  safe_not_equal: Ap,
  svg_element: xp
} = window.__gradio__svelte__internal, {
  SvelteComponent: Sp,
  append_hydration: Bp,
  attr: qp,
  children: Tp,
  claim_svg_element: Ip,
  detach: Rp,
  init: zp,
  insert_hydration: Lp,
  noop: Op,
  safe_not_equal: Pp,
  svg_element: Mp
} = window.__gradio__svelte__internal, {
  SvelteComponent: Np,
  append_hydration: Hp,
  attr: jp,
  children: Gp,
  claim_svg_element: Up,
  detach: Zp,
  init: Xp,
  insert_hydration: Yp,
  noop: Wp,
  safe_not_equal: Qp,
  svg_element: Kp
} = window.__gradio__svelte__internal, {
  SvelteComponent: Vp,
  append_hydration: Jp,
  attr: eh,
  children: th,
  claim_svg_element: nh,
  detach: ih,
  init: ah,
  insert_hydration: oh,
  noop: rh,
  safe_not_equal: sh,
  svg_element: lh
} = window.__gradio__svelte__internal, {
  SvelteComponent: uh,
  append_hydration: ch,
  attr: dh,
  children: _h,
  claim_svg_element: ph,
  detach: hh,
  init: mh,
  insert_hydration: gh,
  noop: fh,
  safe_not_equal: $h,
  svg_element: Dh
} = window.__gradio__svelte__internal, {
  SvelteComponent: vh,
  append_hydration: Fh,
  attr: yh,
  children: bh,
  claim_svg_element: wh,
  detach: Ch,
  init: kh,
  insert_hydration: Eh,
  noop: Ah,
  safe_not_equal: xh,
  svg_element: Sh
} = window.__gradio__svelte__internal, {
  SvelteComponent: Bh,
  append_hydration: qh,
  attr: Th,
  children: Ih,
  claim_svg_element: Rh,
  detach: zh,
  init: Lh,
  insert_hydration: Oh,
  noop: Ph,
  safe_not_equal: Mh,
  svg_element: Nh
} = window.__gradio__svelte__internal, {
  SvelteComponent: Hh,
  append_hydration: jh,
  attr: Gh,
  children: Uh,
  claim_svg_element: Zh,
  detach: Xh,
  init: Yh,
  insert_hydration: Wh,
  noop: Qh,
  safe_not_equal: Kh,
  set_style: Vh,
  svg_element: Jh
} = window.__gradio__svelte__internal, {
  SvelteComponent: em,
  append_hydration: tm,
  attr: nm,
  children: im,
  claim_svg_element: am,
  detach: om,
  init: rm,
  insert_hydration: sm,
  noop: lm,
  safe_not_equal: um,
  svg_element: cm
} = window.__gradio__svelte__internal, {
  SvelteComponent: dm,
  append_hydration: _m,
  attr: pm,
  children: hm,
  claim_svg_element: mm,
  detach: gm,
  init: fm,
  insert_hydration: $m,
  noop: Dm,
  safe_not_equal: vm,
  svg_element: Fm
} = window.__gradio__svelte__internal, {
  SvelteComponent: ym,
  append_hydration: bm,
  attr: wm,
  children: Cm,
  claim_svg_element: km,
  detach: Em,
  init: Am,
  insert_hydration: xm,
  noop: Sm,
  safe_not_equal: Bm,
  svg_element: qm
} = window.__gradio__svelte__internal, {
  SvelteComponent: Tm,
  append_hydration: Im,
  attr: Rm,
  children: zm,
  claim_svg_element: Lm,
  detach: Om,
  init: Pm,
  insert_hydration: Mm,
  noop: Nm,
  safe_not_equal: Hm,
  svg_element: jm
} = window.__gradio__svelte__internal, {
  SvelteComponent: Gm,
  append_hydration: Um,
  attr: Zm,
  children: Xm,
  claim_svg_element: Ym,
  detach: Wm,
  init: Qm,
  insert_hydration: Km,
  noop: Vm,
  safe_not_equal: Jm,
  svg_element: eg
} = window.__gradio__svelte__internal, {
  SvelteComponent: tg,
  append_hydration: ng,
  attr: ig,
  children: ag,
  claim_svg_element: og,
  detach: rg,
  init: sg,
  insert_hydration: lg,
  noop: ug,
  safe_not_equal: cg,
  svg_element: dg
} = window.__gradio__svelte__internal, {
  SvelteComponent: _g,
  append_hydration: pg,
  attr: hg,
  children: mg,
  claim_svg_element: gg,
  detach: fg,
  init: $g,
  insert_hydration: Dg,
  noop: vg,
  safe_not_equal: Fg,
  svg_element: yg
} = window.__gradio__svelte__internal, {
  SvelteComponent: bg,
  append_hydration: wg,
  attr: Cg,
  children: kg,
  claim_svg_element: Eg,
  detach: Ag,
  init: xg,
  insert_hydration: Sg,
  noop: Bg,
  safe_not_equal: qg,
  svg_element: Tg
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ig,
  append_hydration: Rg,
  attr: zg,
  children: Lg,
  claim_svg_element: Og,
  claim_text: Pg,
  detach: Mg,
  init: Ng,
  insert_hydration: Hg,
  noop: jg,
  safe_not_equal: Gg,
  svg_element: Ug,
  text: Zg
} = window.__gradio__svelte__internal, {
  SvelteComponent: Xg,
  append_hydration: Yg,
  attr: Wg,
  children: Qg,
  claim_svg_element: Kg,
  detach: Vg,
  init: Jg,
  insert_hydration: ef,
  noop: tf,
  safe_not_equal: nf,
  svg_element: af
} = window.__gradio__svelte__internal, {
  SvelteComponent: of,
  append_hydration: rf,
  attr: sf,
  children: lf,
  claim_svg_element: uf,
  detach: cf,
  init: df,
  insert_hydration: _f,
  noop: pf,
  safe_not_equal: hf,
  svg_element: mf
} = window.__gradio__svelte__internal, {
  SvelteComponent: gf,
  append_hydration: ff,
  attr: $f,
  children: Df,
  claim_svg_element: vf,
  detach: Ff,
  init: yf,
  insert_hydration: bf,
  noop: wf,
  safe_not_equal: Cf,
  svg_element: kf
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ef,
  append_hydration: Af,
  attr: xf,
  children: Sf,
  claim_svg_element: Bf,
  detach: qf,
  init: Tf,
  insert_hydration: If,
  noop: Rf,
  safe_not_equal: zf,
  svg_element: Lf
} = window.__gradio__svelte__internal, {
  SvelteComponent: Of,
  append_hydration: Pf,
  attr: Mf,
  children: Nf,
  claim_svg_element: Hf,
  detach: jf,
  init: Gf,
  insert_hydration: Uf,
  noop: Zf,
  safe_not_equal: Xf,
  svg_element: Yf
} = window.__gradio__svelte__internal, {
  SvelteComponent: Wf,
  append_hydration: Qf,
  attr: Kf,
  children: Vf,
  claim_svg_element: Jf,
  detach: e0,
  init: t0,
  insert_hydration: n0,
  noop: i0,
  safe_not_equal: a0,
  svg_element: o0
} = window.__gradio__svelte__internal, {
  SvelteComponent: r0,
  append_hydration: s0,
  attr: l0,
  children: u0,
  claim_svg_element: c0,
  detach: d0,
  init: _0,
  insert_hydration: p0,
  noop: h0,
  safe_not_equal: m0,
  svg_element: g0
} = window.__gradio__svelte__internal, {
  SvelteComponent: f0,
  append_hydration: $0,
  attr: D0,
  children: v0,
  claim_svg_element: F0,
  claim_text: y0,
  detach: b0,
  init: w0,
  insert_hydration: C0,
  noop: k0,
  safe_not_equal: E0,
  svg_element: A0,
  text: x0
} = window.__gradio__svelte__internal, {
  SvelteComponent: S0,
  append_hydration: B0,
  attr: q0,
  children: T0,
  claim_svg_element: I0,
  claim_text: R0,
  detach: z0,
  init: L0,
  insert_hydration: O0,
  noop: P0,
  safe_not_equal: M0,
  svg_element: N0,
  text: H0
} = window.__gradio__svelte__internal, {
  SvelteComponent: j0,
  append_hydration: G0,
  attr: U0,
  children: Z0,
  claim_svg_element: X0,
  claim_text: Y0,
  detach: W0,
  init: Q0,
  insert_hydration: K0,
  noop: V0,
  safe_not_equal: J0,
  svg_element: e$,
  text: t$
} = window.__gradio__svelte__internal, {
  SvelteComponent: n$,
  append_hydration: i$,
  attr: a$,
  children: o$,
  claim_svg_element: r$,
  detach: s$,
  init: l$,
  insert_hydration: u$,
  noop: c$,
  safe_not_equal: d$,
  svg_element: _$
} = window.__gradio__svelte__internal, {
  SvelteComponent: p$,
  append_hydration: h$,
  attr: m$,
  children: g$,
  claim_svg_element: f$,
  detach: $$,
  init: D$,
  insert_hydration: v$,
  noop: F$,
  safe_not_equal: y$,
  svg_element: b$
} = window.__gradio__svelte__internal, {
  SvelteComponent: w$,
  append_hydration: C$,
  attr: k$,
  children: E$,
  claim_svg_element: A$,
  detach: x$,
  init: S$,
  insert_hydration: B$,
  noop: q$,
  safe_not_equal: T$,
  svg_element: I$
} = window.__gradio__svelte__internal, {
  SvelteComponent: R$,
  append_hydration: z$,
  attr: L$,
  children: O$,
  claim_svg_element: P$,
  detach: M$,
  init: N$,
  insert_hydration: H$,
  noop: j$,
  safe_not_equal: G$,
  svg_element: U$
} = window.__gradio__svelte__internal, {
  SvelteComponent: Z$,
  append_hydration: X$,
  attr: Y$,
  children: W$,
  claim_svg_element: Q$,
  detach: K$,
  init: V$,
  insert_hydration: J$,
  noop: eD,
  safe_not_equal: tD,
  svg_element: nD
} = window.__gradio__svelte__internal, {
  SvelteComponent: iD,
  append_hydration: aD,
  attr: oD,
  children: rD,
  claim_svg_element: sD,
  detach: lD,
  init: uD,
  insert_hydration: cD,
  noop: dD,
  safe_not_equal: _D,
  svg_element: pD
} = window.__gradio__svelte__internal, {
  SvelteComponent: hD,
  append_hydration: mD,
  attr: gD,
  children: fD,
  claim_svg_element: $D,
  detach: DD,
  init: vD,
  insert_hydration: FD,
  noop: yD,
  safe_not_equal: bD,
  svg_element: wD
} = window.__gradio__svelte__internal, {
  SvelteComponent: CD,
  append_hydration: kD,
  attr: ED,
  children: AD,
  claim_svg_element: xD,
  detach: SD,
  init: BD,
  insert_hydration: qD,
  noop: TD,
  safe_not_equal: ID,
  svg_element: RD
} = window.__gradio__svelte__internal, yn = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], Ze = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
yn.reduce(
  (s, { color: t, primary: e, secondary: n }) => ({
    ...s,
    [t]: {
      primary: Ze[t][e],
      secondary: Ze[t][n]
    }
  }),
  {}
);
const {
  SvelteComponent: zD,
  claim_component: LD,
  create_component: OD,
  destroy_component: PD,
  init: MD,
  mount_component: ND,
  safe_not_equal: HD,
  transition_in: jD,
  transition_out: GD
} = window.__gradio__svelte__internal, { createEventDispatcher: UD } = window.__gradio__svelte__internal, {
  SvelteComponent: ZD,
  append_hydration: XD,
  attr: YD,
  check_outros: WD,
  children: QD,
  claim_component: KD,
  claim_element: VD,
  claim_space: JD,
  claim_text: e1,
  create_component: t1,
  destroy_component: n1,
  detach: i1,
  element: a1,
  empty: o1,
  group_outros: r1,
  init: s1,
  insert_hydration: l1,
  mount_component: u1,
  safe_not_equal: c1,
  set_data: d1,
  space: _1,
  text: p1,
  toggle_class: h1,
  transition_in: m1,
  transition_out: g1
} = window.__gradio__svelte__internal, {
  SvelteComponent: f1,
  attr: $1,
  children: D1,
  claim_element: v1,
  create_slot: F1,
  detach: y1,
  element: b1,
  get_all_dirty_from_scope: w1,
  get_slot_changes: C1,
  init: k1,
  insert_hydration: E1,
  safe_not_equal: A1,
  toggle_class: x1,
  transition_in: S1,
  transition_out: B1,
  update_slot_base: q1
} = window.__gradio__svelte__internal, {
  SvelteComponent: T1,
  append_hydration: I1,
  attr: R1,
  check_outros: z1,
  children: L1,
  claim_component: O1,
  claim_element: P1,
  claim_space: M1,
  create_component: N1,
  destroy_component: H1,
  detach: j1,
  element: G1,
  empty: U1,
  group_outros: Z1,
  init: X1,
  insert_hydration: Y1,
  listen: W1,
  mount_component: Q1,
  safe_not_equal: K1,
  space: V1,
  toggle_class: J1,
  transition_in: ev,
  transition_out: tv
} = window.__gradio__svelte__internal, {
  SvelteComponent: nv,
  attr: iv,
  children: av,
  claim_element: ov,
  create_slot: rv,
  detach: sv,
  element: lv,
  get_all_dirty_from_scope: uv,
  get_slot_changes: cv,
  init: dv,
  insert_hydration: _v,
  null_to_empty: pv,
  safe_not_equal: hv,
  transition_in: mv,
  transition_out: gv,
  update_slot_base: fv
} = window.__gradio__svelte__internal, {
  SvelteComponent: $v,
  check_outros: Dv,
  claim_component: vv,
  create_component: Fv,
  destroy_component: yv,
  detach: bv,
  empty: wv,
  group_outros: Cv,
  init: kv,
  insert_hydration: Ev,
  mount_component: Av,
  noop: xv,
  safe_not_equal: Sv,
  transition_in: Bv,
  transition_out: qv
} = window.__gradio__svelte__internal, { createEventDispatcher: Tv } = window.__gradio__svelte__internal, {
  SvelteComponent: bn,
  attr: wn,
  children: Cn,
  claim_component: kn,
  claim_element: En,
  create_component: An,
  destroy_component: xn,
  detach: Xe,
  element: Sn,
  init: Bn,
  insert_hydration: qn,
  mount_component: Tn,
  noop: In,
  safe_not_equal: Rn,
  transition_in: zn,
  transition_out: Ln
} = window.__gradio__svelte__internal, { onMount: On } = window.__gradio__svelte__internal;
function Pn(s) {
  let t, e, n;
  return e = new Bt({
    props: {
      style: "border-width: 0 !important; padding: 0 !important; margin: 0 !important;"
    }
  }), {
    c() {
      t = Sn("div"), An(e.$$.fragment), this.h();
    },
    l(a) {
      t = En(a, "DIV", { class: !0 });
      var o = Cn(t);
      kn(e.$$.fragment, o), o.forEach(Xe), this.h();
    },
    h() {
      wn(t, "class", "hidden-wrapper svelte-goqrqq");
    },
    m(a, o) {
      qn(a, t, o), Tn(e, t, null), n = !0;
    },
    p: In,
    i(a) {
      n || (zn(e.$$.fragment, a), n = !0);
    },
    o(a) {
      Ln(e.$$.fragment, a), n = !1;
    },
    d(a) {
      a && Xe(t), xn(e);
    }
  };
}
function Mn(s, t, e) {
  let { value: n } = t, a = null, o = !1;
  function i() {
    if (a && !o) {
      const r = document.body, l = "gradio-custom-body-html-container";
      if (!document.getElementById(l)) {
        console.log("[HTMLInjector] Injecting HTML content into the body.");
        const m = document.createElement("div");
        m.id = l, m.innerHTML = a, r.appendChild(m), o = !0;
      }
    }
  }
  return On(() => {
    i();
  }), s.$$set = (r) => {
    "value" in r && e(0, n = r.value);
  }, s.$$.update = () => {
    if (s.$$.dirty & /*value*/
    1 && n) {
      const r = document.head;
      if (n.css) {
        const l = "gradio-custom-head-styles";
        if (!document.getElementById(l)) {
          const m = document.createElement("style");
          m.id = l, m.innerHTML = n.css, r.appendChild(m);
        }
      }
      if (n.js) {
        const l = "gradio-custom-head-script";
        if (!document.getElementById(l)) {
          const m = document.createElement("script");
          m.id = l, m.innerHTML = n.js, r.appendChild(m);
        }
      }
      n.body_html && (a = n.body_html, i());
    }
  }, [n];
}
class Iv extends bn {
  constructor(t) {
    super(), Bn(this, t, Mn, Pn, Rn, { value: 0 });
  }
}
export {
  Iv as default
};
