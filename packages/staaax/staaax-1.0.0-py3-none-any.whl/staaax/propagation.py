import jax.numpy as jnp

def angled_sqrt(x, bc_angle=jnp.pi, nan_tolerance=0):
    """Square root with adjusted direction of the branchcut.

    Args:
        x (complex): Argument of the square root.
        bc_angle (float, optional): Angle of the branchcut. Defaults to pi.
        nan_tolerance (float, optional): Angle around the branchcut, for which to return nan. Defaults to 0.

    Returns:
        complex: Square root of x.
    """
    arg = (bc_angle-jnp.pi)
    adjusted_angle = jnp.angle(x*jnp.exp(1j*arg))

    adjusted_angle = jnp.where(
        jnp.abs(adjusted_angle)<=(jnp.pi-nan_tolerance), 
        adjusted_angle, 
        jnp.nan)
    
    return jnp.sqrt(jnp.abs(x)) * jnp.exp(0.5j * (adjusted_angle - arg)) 

def propagation_kx(ni=1, di=1, k0=1, kx=0, bc_angle=jnp.pi/2, **kwargs):
    """Propagation S-matrix for a homogeneous layer.

    Args:
        ni (complex, optional): Refractive Index. Defaults to 1.
        di (float, optional): Thickness of the layer. Defaults to 1.
        k0 (float, optional): Vacuum Wavenumber. Defaults to 1.
        kx (float, optional): Component of the wavevector parallel to the interfaces. Defaults to 0.
        bc_angle (float, optional): Branchcut angle. Defaults to pi/2.

    Returns:
        sax.SDict: S-matrix of the propagation through the layer.
    """
    kz = angled_sqrt((k0*ni)**2-kx**2 + 0j, bc_angle, nan_tolerance=0)

    prop_i = jnp.exp(1j * kz * di)
    sdict = {
        ("left", "right"): prop_i,
        ("right", "left"): prop_i,
    }
    return sdict