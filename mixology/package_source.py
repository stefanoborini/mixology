import abc

from typing import Any
from typing import Hashable
from typing import List
from typing import Union as _Union

from .constraint import Constraint
from .incompatibility import Incompatibility
from .incompatibility_cause import DependencyCause
from .package import Package
from .range import Range
from .term import Term
from .union import Union


class PackageSourceABC(abc.ABC):
    """
    Provides information about specifications and dependencies to the resolver,
    allowing the VersionResolver class to remain generic while still providing power
    and flexibility.

    This contract contains the methods that users of Mixology must implement
    using knowledge of their own model classes.

    Note that the following concepts needs to be implemented
    in order to make the resolver work as best as possible:


    ## Package

    This user-defined class will be used to represent
    the various packages being resolved.

    __str__() will be called when providing information and feedback,
    in most cases it should return the name of the package.

    It also should implement __eq__ and __hash__.


    ## Version

    This user-defined class will be used to represent a single version.

    Versions of the same package will be compared to each other, however
    they do not need to store their associated package.

    As such they should be comparable. __str__() should also preferably be defined.


    ## Dependency

    This user-defined class represents a requirement of a package to another.

    It is returned by dependencies_for(package, version) and will be passed to
    convert_dependency(dependency) to convert it to a format Mixology understands.

    __eq__() should be defined.
    """

    def __init__(self):  # type: () -> None
        self._root_package = Package.root()

    @property
    def root(self):  # type: () -> Hashable
        return Package.root()

    @property
    @abc.abstractmethod
    def root_version(self):  # type: () -> Any
        """"""

    def versions_for(
        self, package, constraint=None
    ):  # type: (Hashable, Any) -> List[Hashable]
        """
        Search for the specifications that match the given constraint.
        """
        if package == self._root_package:
            return [self.root_version]

        return self._versions_for(package, constraint)

    @abc.abstractmethod
    def _versions_for(self, package, constraint=None):  # type: (Hashable, Any) -> List[Hashable]
        """"""

    @abc.abstractmethod
    def dependencies_for(self, package, version):  # type: (Hashable, Any) -> List[Any]
        """"""

    @abc.abstractmethod
    def convert_dependency(self, dependency):  # type: (Any) -> _Union[Constraint, Range, Union]
        """
        Converts a user-defined dependency (returned by dependencies_for())
        into a format Mixology understands.
        """

    def incompatibilities_for(
        self, package, version
    ):  # type: (Hashable, Any) -> List[Incompatibility]
        """
        Returns the incompatibilities of a given package and version
        """
        dependencies = self.dependencies_for(package, version)
        package_constraint = Constraint(package, Range(version, version, True, True))

        incompatibilities = []
        for dependency in dependencies:
            constraint = self.convert_dependency(dependency)

            if not isinstance(constraint, Constraint):
                constraint = Constraint(package, constraint)

            incompatibility = Incompatibility(
                [Term(package_constraint, True), Term(constraint, False)],
                cause=DependencyCause(),
            )
            incompatibilities.append(incompatibility)

        return incompatibilities


# Preserved for backward compatibility.
class PackageSource(PackageSourceABC):
    @property
    def root_version(self):  # type: () -> Any
        """"""
        raise NotImplementedError()

    @abc.abstractmethod
    def _versions_for(self, package, constraint=None):  # type: (Hashable, Any) -> List[Hashable]
        """"""
        raise NotImplementedError()

    @abc.abstractmethod
    def dependencies_for(self, package, version):  # type: (Hashable, Any) -> List[Any]
        """"""
        raise NotImplementedError()

    def convert_dependency(self, dependency):  # type: (Any) -> _Union[Constraint, Range, Union]
        """
        Converts a user-defined dependency (returned by dependencies_for())
        into a format Mixology understands.
        """
        raise NotImplementedError()
