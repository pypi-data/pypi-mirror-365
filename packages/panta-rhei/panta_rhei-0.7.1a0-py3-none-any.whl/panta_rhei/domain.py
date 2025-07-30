import dolfin as df


class Domain(df.Mesh):
    def __init__(
        self,
        mesh: df.Mesh,
        subdomains: df.MeshFunction,
        boundaries: df.MeshFunction,
        **kwargs,
    ):
        super().__init__(mesh, **kwargs)
        self.subdomains = transfer_meshfunction(self, subdomains)
        self.boundaries = transfer_meshfunction(self, boundaries)


def transfer_meshfunction(
    newmesh: df.Mesh, meshfunc: df.MeshFunction
) -> df.MeshFunction:
    newtags = df.MeshFunction("size_t", newmesh, dim=meshfunc.dim())  # type: ignore
    newtags.set_values(meshfunc)  # type: ignore
    return newtags
