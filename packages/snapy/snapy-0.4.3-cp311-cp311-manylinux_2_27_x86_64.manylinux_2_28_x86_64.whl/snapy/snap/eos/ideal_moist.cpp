// kintere
#include <kintera/constants.h>

#include <kintera/thermo/eval_uhs.hpp>
#include <kintera/thermo/thermo.hpp>

// snap
#include <snap/snap.h>

#include <snap/registry.hpp>

#include "ideal_moist.hpp"

namespace snap {

IdealMoistImpl::IdealMoistImpl(EquationOfStateOptions const &options_)
    : EquationOfStateImpl(options_) {
  reset();
}

void IdealMoistImpl::reset() {
  // set up coordinate model
  pcoord = register_module_op(this, "coord", options.coord());

  // set up thermodynamics model
  pthermo = register_module("thermo", kintera::ThermoY(options.thermo()));

  // populate buffers
  int nc1 = options.coord().nc1();
  int nc2 = options.coord().nc2();
  int nc3 = options.coord().nc3();

  _prim = register_buffer(
      "W", torch::empty({nvar(), nc3, nc2, nc1}, torch::kFloat64));

  _cons = register_buffer(
      "U", torch::empty({nvar(), nc3, nc2, nc1}, torch::kFloat64));

  _gamma = register_buffer("A", torch::empty({nc3, nc2, nc1}, torch::kFloat64));

  _cs = register_buffer("L", torch::empty({nc3, nc2, nc1}, torch::kFloat64));

  _ke = register_buffer("K", torch::empty({nc3, nc2, nc1}, torch::kFloat64));

  _ie = register_buffer("I", torch::empty({nc3, nc2, nc1}, torch::kFloat64));

  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;

  _ce =
      register_buffer("E", torch::empty({ny, nc3, nc2, nc1}, torch::kFloat64));
  _rhoc =
      register_buffer("C", torch::empty({ny, nc3, nc2, nc1}, torch::kFloat64));

  inv_mu_ratio_m1 =
      register_buffer("inv_mu_ratio_m1", torch::zeros({ny}, torch::kFloat64));

  for (int i = 0; i < ny; ++i) {
    inv_mu_ratio_m1[i] = pthermo->inv_mu[i + 1] / pthermo->inv_mu[0] - 1.;
  }

  cv_ratio_m1 =
      register_buffer("cv_ratio_m1", torch::zeros({ny}, torch::kFloat64));

  auto Rd = kintera::constants::Rgas * pthermo->inv_mu[0];
  for (int i = 0; i < ny; ++i) {
    auto Ri = kintera::constants::Rgas * pthermo->inv_mu[i + 1];
    cv_ratio_m1[i] = (pthermo->options.cref_R()[1 + i] * Ri) /
                         (pthermo->options.cref_R()[0] * Rd) -
                     1.;
  }

  u0 = register_buffer(
      "u0", torch::tensor(pthermo->options.uref_R(), torch::kFloat64));

  u0 *= kintera::constants::Rgas * pthermo->inv_mu;
}

torch::Tensor IdealMoistImpl::compute(std::string ab,
                                      std::vector<torch::Tensor> const &args) {
  if (ab == "W->U") {
    _prim2cons(args[0], _cons);
    return _cons;
  } else if (ab == "W->I") {
    _prim2intEng(args[0], _ie);
    return _ie;
  } else if (ab == "W->T") {
    auto temp = get_buffer("thermo.T");
    _prim2temp(args[0], temp);
    return temp;
  } else if (ab == "W->E") {
    _prim2speciesEng(args[0], _ce);
    return _ce;
  } else if (ab == "U->W") {
    _cons2prim(args[0], _prim);
    return _prim;
  } else if (ab == "U->K") {
    _cons2ke(args[0], _ke);
    return _ke;
  } else if (ab == "UT->I") {
    _temp2intEng(args[0], args[1], _ie);
    return _ie;
  } else if (ab == "W->A") {
    auto gammad =
        (pthermo->options.cref_R()[0] + 1) / pthermo->options.cref_R()[0];
    _gamma.set_(gammad * torch::ones_like(args[0][IDN]));
    return _gamma;
  } else if (ab == "WA->L") {
    auto dens = args[0][IDN];
    auto pres = args[0][IPR];
    _cs.set_(torch::sqrt(args[1] * pres / dens));
    return _cs;
  } else {
    TORCH_CHECK(false, "Unknown abbreviation: ", ab);
  }
}

void IdealMoistImpl::_prim2intEng(torch::Tensor prim, torch::Tensor &ie) {
  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;

  auto yfrac = prim.narrow(0, ICY, ny);

  auto gammad =
      (pthermo->options.cref_R()[0] + 1) / pthermo->options.cref_R()[0];

  // TODO(cli) iteration needed here
  ie = prim[IPR] * _fsig(yfrac) / _feps(yfrac) / (gammad - 1);

  // add the internal energy offset
  auto yd = 1. - yfrac.sum(0);
  ie += prim[IDN] * yd * u0[0];
  ie +=
      prim[IDN] * yfrac.unfold(0, ny, 1).matmul(u0.narrow(0, 1, ny)).squeeze(0);
}

void IdealMoistImpl::_prim2cons(torch::Tensor prim, torch::Tensor &cons) {
  apply_primitive_limiter_(prim);
  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;

  // den -> den
  auto out = cons[IDN];
  torch::mul_out(out, (1. - prim.narrow(0, ICY, ny).sum(0)), prim[IDN]);

  // mixr -> den
  out = cons.narrow(0, ICY, ny);
  torch::mul_out(out, prim.narrow(0, ICY, ny), prim[IDN]);

  // vel -> mom
  out = cons.narrow(0, IVX, 3);
  torch::mul_out(out, prim.narrow(0, IVX, 3), prim[IDN]);

  pcoord->vec_lower_(out);

  // KE
  _ke.set_((prim.narrow(0, IVX, 3) * cons.narrow(0, IVX, 3)).sum(0));
  _ke *= 0.5;

  // IE
  _prim2intEng(prim, _ie);

  out = cons[IPR];
  torch::add_out(out, _ke, _ie);

  apply_conserved_limiter_(cons);
}

void IdealMoistImpl::_prim2temp(torch::Tensor prim, torch::Tensor &out) {
  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;
  auto Rd = kintera::constants::Rgas / kintera::species_weights[0];
  auto yfrac = prim.narrow(0, ICY, ny);
  out.set_(prim[IPR] / (prim[IDN] * Rd * _feps(yfrac)));
}

void IdealMoistImpl::_prim2speciesEng(torch::Tensor prim, torch::Tensor &out) {
  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;

  auto mud = kintera::species_weights[0];
  auto Rd = kintera::constants::Rgas / mud;
  auto cvd = kintera::species_cref_R[0] * Rd;

  auto yfrac = prim.narrow(0, ICY, ny);
  auto temp = prim[IPR] / (prim[IDN] * Rd * _feps(yfrac));

  _rhoc.set_(prim[IDN] * yfrac);

  std::vector<int64_t> vec = {ny, 1, 1, 1};
  auto ie = _rhoc * (u0.narrow(0, 1, ny).view(vec) +
                     (cv_ratio_m1.view(vec) + 1.) * cvd * temp);

  auto vel = prim.narrow(0, IVX, 3).clone();
  pcoord->vec_lower_(vel);
  auto ke = 0.5 * (prim.narrow(0, IVX, 3) * vel).sum(0, /*keepdim=*/true);

  out.set_(ie + ke * _rhoc);
}

void IdealMoistImpl::_cons2prim(torch::Tensor cons, torch::Tensor &prim) {
  apply_conserved_limiter_(cons);

  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;

  // den -> den
  auto out = prim[IDN];
  torch::sum_out(out, cons.narrow(0, ICY, ny), /*dim=*/0);
  out += cons[IDN];

  // den -> mixr
  out = prim.narrow(0, ICY, ny);
  torch::div_out(out, cons.narrow(0, ICY, ny), prim[IDN]);

  // mom -> vel
  out = prim.narrow(0, IVX, 3);
  torch::div_out(out, cons.narrow(0, IVX, 3), prim[IDN]);

  pcoord->vec_raise_(out);

  _ke.set_((prim.narrow(0, IVX, 3) * cons.narrow(0, IVX, 3)).sum(0));
  _ke *= 0.5;

  torch::sub_out(_ie, cons[IPR], _ke);

  // subtract the internal energy offset
  _ie -= cons[IDN] * u0[0];

  std::vector<int64_t> vec(cons.dim(), 1);
  vec[0] = -1;
  _ie -= (cons.narrow(0, ICY, ny) * u0.narrow(0, 1, ny).view(vec)).sum(0);

  // eng -> pr
  auto gammad =
      (pthermo->options.cref_R()[0] + 1) / pthermo->options.cref_R()[0];

  // TODO(cli) iteration needed here
  auto yfrac = prim.narrow(0, ICY, ny);
  prim[IPR] = (gammad - 1) * _ie * _feps(yfrac) / _fsig(yfrac);

  apply_primitive_limiter_(prim);
}

void IdealMoistImpl::_cons2ke(torch::Tensor cons, torch::Tensor &out) {
  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;
  auto rho = get_buffer("thermo.D");
  rho.set_(cons[IDN] + cons.narrow(0, ICY, ny).sum(0));

  auto mom = cons.narrow(0, IVX, 3).clone();
  pcoord->vec_raise_(mom);
  out.set_(0.5 * (cons.narrow(0, IVX, 3) * mom).sum(0) / rho);
}

void IdealMoistImpl::_temp2intEng(torch::Tensor cons, torch::Tensor temp,
                                  torch::Tensor &out) {
  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;

  // internal energy offset
  _ie = cons[IDN] * u0[0];

  std::vector<int64_t> vec(cons.dim(), 1);
  vec[0] = -1;
  _ie += (cons.narrow(0, ICY, ny) * u0.narrow(0, 1, ny).view(vec)).sum(0);

  auto mud = kintera::species_weights[0];
  auto Rd = kintera::constants::Rgas / mud;
  auto cvd = kintera::species_cref_R[0] * Rd;
  auto cvy = (cv_ratio_m1 + 1.) * cvd;

  _ie += (cons.narrow(0, ICY, ny) * cvy.view(vec)).sum(0);
  _ie *= temp;
}

torch::Tensor IdealMoistImpl::_feps(torch::Tensor const &yfrac) const {
  int nvapor = pthermo->options.vapor_ids().size() - 1;
  int ncloud = pthermo->options.cloud_ids().size();

  if (nvapor == 0 && ncloud == 0) {
    auto vec = yfrac.sizes().vec();
    vec.erase(vec.begin());
    return torch::ones(vec, yfrac.options());
  }

  auto yu = yfrac.narrow(0, 0, nvapor).unfold(0, nvapor, 1);
  return 1. + yu.matmul(inv_mu_ratio_m1.narrow(0, 0, nvapor)).squeeze(0) -
         yfrac.narrow(0, nvapor, ncloud).sum(0);
}

torch::Tensor IdealMoistImpl::_fsig(torch::Tensor const &yfrac) const {
  int ny = pthermo->options.vapor_ids().size() +
           pthermo->options.cloud_ids().size() - 1;

  if (ny == 0) {
    auto vec = yfrac.sizes().vec();
    vec.erase(vec.begin());
    return torch::ones(vec, yfrac.options());
  }

  auto yu = yfrac.unfold(0, ny, 1);
  return 1. + yu.matmul(cv_ratio_m1).squeeze(0);
}

}  // namespace snap
