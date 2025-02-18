from math import *
import numpy as np
from colour import Color
import plotly.express as px
import httplib2
import string as st
from scipy.linalg import null_space
from scipy.spatial import KDTree
from stl import mesh
import pywavefront as py_obj
import collada as py_col
from httplib2 import *


class Utils:
    """A library that contains some utilities for UAIbot. All of the functions are static."""

    #######################################
    # Constants
    #######################################

    _PI = 3.1415926
    _SQRTHALFPI = 1.2533141
    _SQRT2 = 1.4142135
    _CONSTJA = 2.7889
    _CONSTI0HAT1 = 0.24273
    _CONSTI0HAT2 = 0.43023

    UAIBOT_NAME_TYPES = ['uaibot.', 'cylinder.', 'box.', 'ball.', 'robot.', 'simulation.', 'meshmaterial.',
                             'texture.',
                             'pointlight.', 'frame.', 'model3d.', 'links.', 'pointcloud.', 'vector.', 'rigidobject.',
                             '.group', '.htmldiv']

    IS_SIMPLE = ['uaibot.Ball', 'uaibot.Box', 'uaibot.Cylinder']

    IS_GROUPABLE = ['uaibot.Ball', 'uaibot.Box', 'uaibot.Cylinder', 'uaibot.Frame',
                    'uaibot.RigidObject', 'uaibot.Group', 'uaibot.Robot', 'uaibot.PointLight']

    IS_OBJ_SIM = ['uaibot.Ball', 'uaibot.Box', 'uaibot.Cylinder', 'uaibot.Robot',
                  'uaibot.PointLight', 'uaibot.Frame', 'uaibot.PointCloud', 'uaibot.Vector',
                  'uaibot.RigidObject', 'uaibot.Group', 'uaibot.HTMLDiv']

    #######################################
    # Basic functions
    #######################################

    @staticmethod
    def S(v):
        """
      Returns a 3x3 matrix that implements the cross product for a 3D vector  
      as a matricial product, that is, a matrix S(v) such that for any other 
      3D column  vector w, S(v)w = cross(v,w).
      
      Parameters
      ----------
      v : a 3D vector
          The vector for which the S matrix will be created.

      Returns
      -------
      S : 3x3 numpy matrix
          A matrix that implements the cross product with v.
      """
        vv = np.matrix(v).reshape((3,1))
        return np.matrix([[0, -vv[2,0], vv[1,0]],
                         [vv[2,0], 0, -vv[0,0]],
                         [-vv[1,0], vv[0,0], 0]])

    @staticmethod
    def rot(axis, angle):
        """
      Homogeneous transformation matrix that represents the rotation of an
      angle in an axis.
      
      Parameters
      ----------
      axis : a 3D vector
          The axis of rotation.
      
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      htm : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """
        a = np.reshape(axis, (3,))
        a = a / np.linalg.norm(a)
        K = Utils.S(a)
        Q = np.identity(3) + sin(angle) * K + (1 - cos(angle)) * (K @ K)
        return np.hstack([np.vstack([Q, np.matrix([0, 0, 0])]), np.matrix([[0], [0], [0], [1]])])

    @staticmethod
    def trn(vector):
        """
      Homogeneous transformation matrix that represents the displacement
      of a vector
      
      Parameters
      ----------
      vector : a 3D vector
          The displacement vector.
      
      Returns
      -------
      htm : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """
        v = np.matrix(vector).reshape((3,1))
        return np.matrix([[1, 0, 0, v[0,0]],
                         [0, 1, 0, v[1,0]],
                         [0, 0, 1, v[2,0]],
                         [0, 0, 0, 1]])

    @staticmethod
    def rotx(angle):
        """
      Homogeneous transformation matrix that represents the rotation of an
      angle in the 'x' axis.
      
      Parameters
      ----------
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      htm : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """
        return np.matrix([[1, 0, 0, 0],
                         [0, cos(angle), -sin(angle), 0],
                         [0, sin(angle), cos(angle), 0],
                         [0, 0, 0, 1]])

    @staticmethod
    def roty(angle):
        """
      Homogeneous transformation matrix that represents the rotation of an
      angle in the 'y' axis.
      
      Parameters
      ----------
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      htm : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """
        return np.matrix([[cos(angle), 0, sin(angle), 0],
                         [0, 1, 0, 0],
                         [-sin(angle), 0, cos(angle), 0],
                         [0, 0, 0, 1]])

    @staticmethod
    def rotz(angle):
        """
      Homogeneous transformation matrix that represents the rotation of an
      angle in the 'z' axis.
      
      Parameters
      ----------
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      htm : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """
        return np.matrix([[cos(angle), -sin(angle), 0, 0],
                         [sin(angle), cos(angle), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])

    @staticmethod
    def inv_htm(htm):
        """
      Given an homogeneous transformation matrix, compute its inverse.
      It is faster than using numpy.linalg.inv in the case of HTMs.
      
      Parameters
      ----------
      htm: 4X4 numpy array or nested list 
          Homogeneous transformation matrix of the rotation.

      Returns
      -------
      inv_htm: 4X4 numpy array
          The inverse of the transformation matrix.       
      """
        Q = htm[0:3, 0:3]
        p = htm[0:3, 3]

        inv_htm = np.matrix(np.zeros((4, 4)))
        inv_htm[0:3, 0:3] = Q.T
        inv_htm[0:3, 3] = - Q.T * p
        inv_htm[3, 3] = 1

        return np.matrix(inv_htm)

    @staticmethod
    def axis_angle(htm):
        """
      Given an homogeneous transformation matrix representing a rotation, 
      return the rotation axis angle.
      
      Parameters
      ----------
      htm: 4X4 numpy array or nested list 
          Homogeneous transformation matrix of the rotation.

      Returns
      -------
      axis : 3D numpy vector
          The rotation axis.

      angle : float
          The rotation angle, in radians.        
      """
        Q = htm[0:3, 0:3]
        trace = Q[0, 0] + Q[1, 1] + Q[2, 2]
        angle = acos((trace - 1) / 2)
        G = Q @ Q - 2 * cos(angle) * Q + np.identity(3)
        ok = False
        while not ok:
            v = np.matrix(np.random.uniform(-100, 100, size=(3,1)))
            w = np.matrix(np.random.uniform(-100, 100, size=(3,1)))
            r = G * v
            nr = np.linalg.norm(r)
            prod = w.T * r
            if nr > 0.01:
                ortr = w -  (r * prod) / (nr * nr)
                axis = Utils.S(ortr) * (Q * ortr)
                naxis = np.linalg.norm(axis)
                ok = naxis > 0.01

        axis = axis / naxis
        return axis, angle

    @staticmethod
    def euler_angles(htm):

        Q = np.matrix(htm[0:3, 0:3])
        sy = sqrt(Q[0, 0] ** 2 + Q[1, 0] ** 2)

        if abs(sy) > 0.001:
            gamma = np.arctan2(Q[2, 1], Q[2, 2])
            beta = np.arctan2(-Q[2, 0], sy)
            alpha = np.arctan2(Q[1, 0], Q[0, 0])
        else:
            gamma = np.arctan2(-Q[1, 2], Q[1, 1])
            beta = np.arctan2(-Q[2, 0], sy)
            alpha = 0

        return alpha, beta, gamma

    @staticmethod
    def dp_inv(mat, eps = 0.001):
        """
      Compute the damped pseudoinverse of the matrix 'mat''.
      
      Parameters
      ----------
      mat: nxm numpy array
          The matrix to compute the damped pseudoinverse.
      
      eps: positive float
          The damping factor.
          (default: 0.001).

      Returns
      -------
      pinvA: mxn numpy array
          The damped pseudoinverse of 'mat'.
      """
        n = np.shape(mat)[1]
        return np.linalg.inv(mat.T * mat + eps * np.identity(n)) * mat.T

    @staticmethod
    def jac(f, x, delta=0.0001):
        """
      Compute the numerical Jacobian of a function f at the point x.
      Uses centralized finite difference to compute the derivatives.
      
      Parameters
      ----------
      f: function handle
          The function handle. It should accept a single 'm' dimensional list
          of floats and returns a single 'n' dimensional list of floats.
      
      x: m dimensional numpy vector or list
          Point in which the Jacobian will be computed.

      delta: float
          Variation used in the numerical differentiation
          (default: 0.0001)

      Returns
      -------
      jac: n x m numpy array
          The numerical Jacobian of f at point x. It is a n x m numpy array.
      """

        if not (str(type(f)) == "<class 'function'>"):
            raise Exception("The parameter 'f' must be a function that maps 'm' dimensional lists" \
                            ", in which 'm' is the size of the vector 'x', into 'n' dimensional lists.")

        if not Utils.is_a_vector(x):
            raise Exception("Parameter 'x' should be a vector")

        if str(type(x)) == "<class 'numpy.ndarray'>":
            m = max(np.shape(x))

        if str(type(x)) == "<class 'list'>":
            m = len(x)

        try:
            y = f(x)

            if str(type(y)) == "<class 'list'>" and Utils.is_a_vector(y):
                n = len(y)
            else:
                raise Exception("The parameter 'f' must be a function that maps 'm' dimensional vectors" \
                                ", in which 'm' is the size of the vector 'x', into 'n' dimensional vectors.")
        except:
            raise Exception("The parameter 'f' must be a function that maps 'm' dimensional vectors" \
                            ", in which 'm' is the size of the vector 'x', into 'n' dimensional vectors.")

        jac = np.matrix(np.zeros((n, m)))
        idm = np.matrix(np.identity(m))

        for j in range(m):
            yp = f(x + idm[:, j] * delta)
            yn = f(x - idm[:, j] * delta)
            jac[:, j] = (yp - yn) / (2 * delta)

        return jac

    @staticmethod
    def signed_shape_pow(x, x_bar, n):
        """
      Compute the following function, for x>=0

      x^n/(x_bar^(n-1)*n) for x <= x_bar
      x + (1/n-1)*x_bar   for x >  x_bar

      The function is continuous. It is also differentiable once, except for
      n<1 at x=0.

      For x<=0, returns -signed_shape_pow(abs(x), x_bar, n), so the function
      is odd.

      This function is useful in control.

      Parameters
      ----------
      x: float
          Argument of the function.

      x_bar: positive float
          Parameter of the function.

      n: positive float
          Parameter of the function.

      Returns
      -------
      y: float
          The return of the function.
      """

        if x >= 0:
            if x <= x_bar:
                return pow(x, n) / (pow(x_bar, n - 1) * n)
            else:
                return x + (1 / n - 1) * x_bar
        else:
            return -Utils.signed_shape_pow(abs(x), x_bar, n)

    @staticmethod
    def hierarchical_solve(mat_a, mat_b, eps=0.001):
        """
      Solve the lexicographical unconstrained quadratic optimization problem

      lexmin_x ||mat_a[i]*x - b[i]||² + eps*||x||²

      with lower indexes having higher priority than higher indexes.

      Parameters
      ----------
      mat_a: A list of matrices (double arrays or numpy matrices).
          The matrices mat_a[i]. All must have the same number of columns.

      mat_b: A list of column vectors (double arrays or numpy matrices).
          The vectors mat_b[i]. The number of rows of mat_b[i] must be equal to the number
          of rows of mat_a[i].

      eps: positive float
          Damping parameter.
          (default: 0.001).

      Returns
      -------
      x: numpy column vector
          The solution x. For positive eps, the solution is always unique.
      """


        x_sol = Utils.dp_inv(mat_a[0], eps) * mat_b[0]

        if len(mat_a) > 1:

            null_mat_a = null_space(mat_a[0])

            if np.shape(null_mat_a)[1] > 0:
                mat_a_mod = []
                mat_b_mod = []
                for i in range(1, len(mat_a)):
                    mat_a_mod.append(mat_a[i] * null_mat_a)
                    mat_b_mod.append(mat_b[i] - mat_a[i] * x_sol)

                y_sol = Utils.hierarchical_solve(mat_a_mod, mat_b_mod, eps)
                return x_sol + null_mat_a * y_sol
            else:
                return x_sol
        else:
            return x_sol


    @staticmethod
    def interpolate(points):
        """
      Create a function handle that generates an one-tme differentiable interpolated data from 'points'.

      The simplest case in when 'points' is a list with m elements. In this case, it will output a function f.
      When this function is evaluated at a scalar t, it will coincide with points[i] when t = i/m, that is,
      f(i/m) = points[i]. This function is once differentiable and periodic with period 1, so f(t+k)=f(t) for
      an integer k.

      The function can also use a n x m numpy array or lists as 'points'. In this case, f(t) is a n dimensional
      column vector in which its i-th entry is the same as computing f_i = interpolate(points[i]) and then
      computing f_i(t).

      Finally, t can be a list of k elements instead of just a scalar. In this case, f(t) is a n x k numpy matrix
      in which the element at row i and column j is the same as computing f_i = interpolate(points[i]) and then
      computing f_i(t[k]).


      Parameters
      ----------
      points: a n x m numpy array or lists
          Points to be interpolated.

      Returns
      -------
      f: function handle
          The function handle that implements the interpolation.
      """

        if not Utils.is_a_matrix(points):
            raise Exception("The parameter 'points' should be a n x m numpy array of numbers.")

        def aux_interpolate_single(arg_points):

            def int_aux_simp(arg_t, arg_n, arg_c):
                tn = arg_n * (arg_t % 1)
                ti = floor(tn)
                coef = arg_c[4 * ti: 4 * ti + 5]
                return coef[0] + coef[1] * tn + coef[2] * tn ** 2 + coef[3] * tn ** 3

            def int_aux(arg_t, arg_n, arg_c):
                return [int_aux_simp(tt, arg_n, arg_c) for tt in arg_t] if str(
                    type(arg_t)) == "<class 'list'>" else int_aux_simp(arg_t, arg_n, arg_c)

            n = len(arg_points)
            xn = np.array(arg_points).tolist()
            xn.append(arg_points[0])

            t = range(n + 1)
            A = np.zeros((3 * n, 4 * n))
            b = np.zeros((3 * n, 1))

            # Equality at initial points
            for p in range(n):
                A[p, 4 * p] = 1
                A[p, 4 * p + 1] = t[p]
                A[p, 4 * p + 2] = t[p] ** 2
                A[p, 4 * p + 3] = t[p] ** 3
                b[p] = xn[p]
            # Equality at final points
            for p in range(n):
                A[n + p, 4 * p] = 1
                A[n + p, 4 * p + 1] = t[p + 1]
                A[n + p, 4 * p + 2] = t[p + 1] ** 2
                A[n + p, 4 * p + 3] = t[p + 1] ** 3
                b[n + p] = xn[p + 1]
            # Equality of the derivative in the initial points
            for p in range(n):
                if not (p == n - 1):
                    A[2 * n + p, 4 * p] = 0
                    A[2 * n + p, 4 * p + 1] = 1
                    A[2 * n + p, 4 * p + 2] = 2 * t[p + 1]
                    A[2 * n + p, 4 * p + 3] = 3 * t[p + 1] ** 2
                    A[2 * n + p, 4 * (p + 1)] = -0
                    A[2 * n + p, 4 * (p + 1) + 1] = -1
                    A[2 * n + p, 4 * (p + 1) + 2] = -2 * t[p + 1]
                    A[2 * n + p, 4 * (p + 1) + 3] = -3 * t[p + 1] ** 2
                else:
                    A[2 * n + p, 4 * p] = 0
                    A[2 * n + p, 4 * p + 1] = 1
                    A[2 * n + p, 4 * p + 2] = 2 * t[p + 1]
                    A[2 * n + p, 4 * p + 3] = 3 * t[p + 1] ** 2
                    A[2 * n + p, 0] = -0
                    A[2 * n + p, 1] = -1
                    A[2 * n + p, 2] = 0
                    A[2 * n + p, 3] = 0

            # Create the objective function

            H = np.zeros((0, 0))
            for p in range(n):
                M = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 4, 6 * ((p + 1) ** 2 - p ** 2)],
                              [0, 0, 6 * ((p + 1) ** 2 - p ** 2), 12 * ((p + 1) ** 3 - p ** 3)]])
                nn = np.shape(H)[0]
                H = np.block([[H, np.zeros((nn, 4))], [np.zeros((4, nn)), M]])

            # Solve the optimization problem
            m1 = np.shape(A)[0]
            m2 = np.shape(A)[1]

            G = np.block([[H, np.transpose(A)], [A, np.zeros((m1, m1))]])
            g = np.block([[np.zeros((m2, 1))], [b]])
            y = np.linalg.solve(G, g)
            c = y[0: np.shape(H)[0]]
            c = c.reshape((1, np.shape(H)[0]))[0].tolist()

            # Create the function
            f = lambda ts: int_aux(ts, n, c)
            return f

        def aux_interpolate_multiple(arg_points, t):

            if not (Utils.is_a_vector(t) or Utils.is_a_number(t)):
                raise Exception(
                    "The parameter of the interpolation function must be either a number or a list of numbers.")

            y = np.zeros((0, len(t) if Utils.is_a_vector(t) else 1))
            for i in range(np.shape(arg_points)[0]):
                fun = aux_interpolate_single(arg_points[i])
                fun_out = fun(t)
                fun_out = np.array(fun_out).reshape((1, len(fun_out)))
                y = np.block([[y], [fun_out]])

            return np.matrix(y)

        return lambda t: aux_interpolate_multiple(points, t)

    #######################################
    # 3d objects manipulation
    #######################################

    @staticmethod
    def _dist_triangle_point(point, triangle):

        v0 = triangle[0,:].reshape((3,1))
        v1 = triangle[1,:].reshape((3,1))
        v2 = triangle[2,:].reshape((3,1))

        A = np.block([v1-v0,v2-v0])
        b = np.array(point).reshape((3,1))-v0

        #Create the solutions

        list_x = []

        list_x.append(np.linalg.inv(np.transpose(A) @ A) @ (np.transpose(A) @ b))

        prod0 = np.transpose(A[:, 0]) @ A[:, 0]
        prod1 = np.transpose(A[:, 1]) @ A[:, 1]

        val = float((np.transpose(A[:, 0]) @ b) / prod0)
        list_x.append(np.array([[val],[0]]))

        val = float((np.transpose(A[:, 1]) @ b) / prod1)
        list_x.append(np.array([[0], [val]]))

        val = float((np.transpose(A[:, 0]) @ (b-A[:, 1].reshape((3,1)))) / prod0)
        list_x.append(np.array([[val], [1]]))

        val = float((np.transpose(A[:, 1]) @ (b-A[:, 0].reshape((3,1)))) / prod1)
        list_x.append(np.array([[1], [val]]))

        list_x.append(np.array([[0],[0]]))
        list_x.append(np.array([[0],[1]]))
        list_x.append(np.array([[1],[0]]))
        list_x.append(np.array([[1],[1]]))

        val_min = float('inf')

        for i in range(9):
            if 1 >= list_x[i][0] >= 0 and 1 >= list_x[i][1]>=0:
                val_min = min(val_min,np.linalg.norm(A @ list_x[i] - b))

        return val_min

    @staticmethod
    def _distance_surface(point, mesh_triangle, kd_tree):

        PARAM_NO_KD_TREE = 30

        _, ind = kd_tree.query(point,PARAM_NO_KD_TREE)
        list_val = []
        for i in range(PARAM_NO_KD_TREE):
            list_val.append(Utils._dist_triangle_point(point,mesh_triangle[ind[i]]))

        val_min = min(list_val)
        return val_min

        #sum_exp=0
        #for i in range(PARAM_NO_KD_TREE):
        #    sum_exp+= exp(-(list_val[i]-val_min)/(h*h))
        #
        #return val_min - h * h * log(sum_exp/PARAM_NO_KD_TREE)

    @staticmethod
    def generate_connectivity_info(mesh_triangle, h):

        PARAM_NO_POINTS_GRAPH = 300
        PARAM_PERCENTAGE = 0.01

        #Compute the limits
        n = len(mesh_triangle)

        xmin = float('inf')
        ymin = float('inf')
        zmin = float('inf')
        xmax = -float('inf')
        ymax = -float('inf')
        zmax = -float('inf')

        triangle_center=[]

        for i in range(n):
            xmin = min(xmin,mesh_triangle[i][0,0],mesh_triangle[i][1,0],mesh_triangle[i][2,0])
            xmax = max(xmax,mesh_triangle[i][0,0],mesh_triangle[i][1,0],mesh_triangle[i][2,0])
            ymin = min(ymin,mesh_triangle[i][0,1],mesh_triangle[i][1,1],mesh_triangle[i][2,1])
            ymax = max(ymax,mesh_triangle[i][0,1],mesh_triangle[i][1,1],mesh_triangle[i][2,1])
            zmin = min(zmin,mesh_triangle[i][0,2],mesh_triangle[i][1,2],mesh_triangle[i][2,2])
            zmax = max(zmax,mesh_triangle[i][0,2],mesh_triangle[i][1,2],mesh_triangle[i][2,2])
            triangle_center.append( (mesh_triangle[i][0,:]+mesh_triangle[i][1,:]+mesh_triangle[i][2,:])/3)

        kd_tree = KDTree(triangle_center)
        dx = xmax - xmin
        dy = ymax - ymin
        dz = zmax - zmin
        limits = [xmin-0.15*dx, xmax+0.15*dx, ymin-0.15*dy, ymax+0.15*dy, zmin-0.15*dz, zmax+0.15*dz ]

        points_inside=[]
        points_outside =[]

        for i in range(2):
            for j in range(2):
                for k in range(2):
                    points_outside.append(np.array([limits[i], limits[2+j], limits[4+k]]))

        def gen_point():
            x = np.random.uniform(limits[0], limits[1])
            y = np.random.uniform(limits[2], limits[3])
            z = np.random.uniform(limits[4], limits[5])
            return np.array([x,y,z])


        def eval_fun(point):
            return Utils._distance_surface(point,mesh_triangle, kd_tree)

        EPSILON_DIST = PARAM_PERCENTAGE * max(dx,dy,dz)

        def line_is_free(point_1,point_2):
            dist_1 = eval_fun(point_1)
            if dist_1 <= EPSILON_DIST:
                return False

            dist_2 = eval_fun(point_2)
            if dist_2 <= EPSILON_DIST:
                return False

            dist_points = np.linalg.norm(point_1 - point_2)
            delta = (dist_1 - dist_2 + dist_points) / 2

            if dist_points < 0.5*EPSILON_DIST:
                return True

            if dist_1 - delta > 2*EPSILON_DIST:
                return True
            else:
                point_middle = (point_1+point_2)/2
                return line_is_free(point_1,point_middle) and line_is_free(point_middle, point_2)



        #Generate a list of points outside
        while len(points_outside) < PARAM_NO_POINTS_GRAPH/2:
            rand_point = gen_point()
            rand_point_outside = points_outside[np.random.randint(0,len(points_outside))]
            if line_is_free(rand_point,rand_point_outside):
                points_outside.append(rand_point)
                print(len(points_outside))

        #Generate a single point inside
        while len(points_inside)==0:
            rand_point = gen_point()
            if eval_fun(rand_point) >  EPSILON_DIST:
                connected_with_outside = False
                j = 0
                while not connected_with_outside and (j < len(points_outside)):
                    connected_with_outside = line_is_free(rand_point,points_outside[j])
                    j+= 1

                if not connected_with_outside:
                    points_inside.append(rand_point)

        print("Point inside found!")
        #Generate other points inside
        while len(points_inside) < PARAM_NO_POINTS_GRAPH/2:
            rand_point = gen_point()
            rand_point_inside = points_inside[np.random.randint(0,len(points_inside))]
            if line_is_free(rand_point,rand_point_inside):
                points_inside.append(rand_point)
                print(len(points_inside))
            else:
                print("Failed!")





        return kd_tree, limits, points_outside, points_inside



    @staticmethod
    def get_data_from_model(path):
        type = path[path.rfind(".") + 1:len(path) + 1]

        points = np.zeros((0,3))
        triangle = []

        if type=="obj":
            mesh_data = py_obj.Wavefront(path,encoding="iso-8859-1",parse=False,create_materials=True,collect_faces=True)
            mesh_data.parse()

            n = len(mesh_data.vertices)
            points = np.zeros((n, 3))
            for i in range(n):
                points[i, 0] = mesh_data.vertices[i][0]
                points[i, 1] = mesh_data.vertices[i][1]
                points[i, 2] = mesh_data.vertices[i][2]

            for i in range(len(mesh_data.mesh_list)):
                for j in range(len(mesh_data.mesh_list[i].faces)):
                    i1 = mesh_data.mesh_list[i].faces[j][0]
                    i2 = mesh_data.mesh_list[i].faces[j][1]
                    i3 = mesh_data.mesh_list[i].faces[j][2]
                    tri = np.block([ [points[i1,:]],  [points[i2,:]],  [points[i3,:]]])
                    triangle.append(tri)

        if type=="stl":

            mesh_data = mesh.Mesh.from_file(path)
            points = np.unique(mesh_data.vectors.reshape((int(mesh_data.vectors.size/3),3)), axis=0)
            triangle = mesh_data.vectors

        if type=="dae":

            mesh_data = py_col.Collada(path)
            for i in range(len(mesh_data.geometries)):
                for j in range(len(mesh_data.geometries[i].primitives[0])):
                    tri = mesh_data.geometries[i].primitives[0][j].vertices
                    triangle.append(tri)
                    points = np.block([[points],[tri]])

            points = np.unique(points,axis=0)

        return points, triangle

    #######################################
    # Type check functions
    #######################################

    @staticmethod
    def is_a_number(obj):
        """
      Check if the argument is a float or int number
      
      Parameters
      ----------
      obj: object
          Object to be verified.
      
      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """

        return str(type(obj)) in ["<class 'int'>", "<class 'float'>", "<class 'numpy.float64'>"]

    @staticmethod
    def is_a_natural_number(obj):
        """
      Check if the argument is a natural number (integer and >=0)
      
      Parameters
      ----------
      obj: object
          Object to be verified.
      
      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """

        return str(type(obj)) == "<class 'int'>" and obj >= 0

    @staticmethod
    def is_a_matrix(obj, n=None, m=None):
        """
      Check if the argument is a nxm matrix of floats.
      
      Parameters
      ----------
      obj: object
          Object to be verified.

      n: positive int
          Number of rows
          (default: it does not matter).

      m: positive int
          Number of columns
          (default: it does not matter).

      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """

        if str(type(obj)) == "<class 'numpy.ndarray'>" or str(type(obj)) == "<class 'numpy.matrix'>":
            return Utils.is_a_matrix(obj.tolist(), n, m)
        else:
            if str(type(obj)) == "<class 'list'>":

                is_all_a_num = True
                is_all_a_list = True

                for obj_el in obj:
                    is_all_a_num = is_all_a_num and Utils.is_a_number(obj_el)
                    is_all_a_list = is_all_a_list and (str(type(obj_el)) == "<class 'list'>")

                if is_all_a_num or is_all_a_list:

                    if is_all_a_num:
                        return ((m is None) or (m == len(obj))) and ((n == 1) or (n is None))

                    if is_all_a_list:
                        if (n is None) or (len(obj) == n):

                            m0 = len(obj[0])

                            if (m is None) or (m == m0):
                                is_correct = True
                                for obj_el in obj:
                                    is_correct = is_correct and len(obj_el) == m0
                                    if is_correct:
                                        for j in range(len(obj_el)):
                                            is_correct = is_correct and Utils.is_a_number(obj_el[j])

                                return is_correct
                            else:
                                return False
                        else:
                            return False
                else:
                    return False
            else:
                return False

    @staticmethod
    def is_a_vector(obj, n=None):
        """
      Check if the argument is a n vector of floats.
      
      Parameters
      ----------
      obj: object
          Object to be verified.

      n: positive int
          Number of elements
          (default: it does not matter).

      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """
        return Utils.is_a_matrix(obj, n, 1) or Utils.is_a_matrix(obj, 1, n)

    @staticmethod
    def is_a_pd_matrix(obj, n=None):
        """
      Check if the argument is a symmetric nxn positive (semi)-definite matrix.
      
      Parameters
      ----------
      obj: object
          Object to be verified.

      n: positive int
          Dimension of the square matrix
          (default: it does not matter).
    
      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """
        value = Utils.is_a_matrix(obj, n, n)

        if value:
            value = np.allclose(obj, np.transpose(obj), rtol=1e-05, atol=1e-08)

        if value:
            try:
                np.linalg.cholesky(obj)
            except:
                value = False

        return value

    @staticmethod
    def is_a_color(obj):
        """
      Check if the argument is a HTML-compatible string that represents a color.
      
      Parameters
      ----------
      obj: object
          Object to be verified.
      
      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """

        try:
            obj = obj.replace(" ", "")
            Color(obj)
            return True
        except:
            return False

    @staticmethod
    def is_a_name(string):
        """
      Check if the argument is a valid name for uaibot objects.
      Only characters [a-z], [A-z], [0-9] and '_' are allowed.
      However, variables should not begin with numbers.

      Parameters
      ----------
      string: string
          Name to be verified.

      Returns
      -------
      is_name: boolean
          If the name is a valid name.
      """

        if str(type(string)) == "<class 'str'>":
            allowed1 = set(st.ascii_lowercase + st.ascii_uppercase + st.digits + "_")
            allowed2 = set(st.ascii_lowercase + st.ascii_uppercase + "_")

            return (set(string) <= allowed1) and (set(string[0]) <= allowed2)
        else:
            return False

    @staticmethod
    def get_uaibot_type(obj):
        """
      Return the uaibot type of the object. 
      Return the empty string if it is not a uaibot object.
      
      Parameters
      ----------
      obj: object
          Object to be verified.
      
      Returns
      -------
      obj_type: string
          uaibot type.   
      """
        type_str = str(type(obj))

        ind = -1
        k = 0
        while ind == -1 and k < len(Utils.UAIBOT_NAME_TYPES):
            ind = type_str.find(Utils.UAIBOT_NAME_TYPES[k])
            k += 1

        if ind == -1:
            return ""
        else:
            ind1 = type_str.rfind('.')
            ind2 = type_str.rfind('>')
            return "uaibot." + type_str[ind1 + 1:ind2 - 1]

    @staticmethod
    def is_a_simple_object(obj):
        """
      Check if the argument is a simple object.
      Check the constant 'Utils.IS_SIMPLE' for a list of simple objects.

      Parameters
      ----------
      obj: object
          Object to be verified.

      Returns
      -------
      is_type: boolean
          If the object is of the type.
      """
        return Utils.get_uaibot_type(obj) in Utils.IS_SIMPLE

    @staticmethod
    def is_a_groupable_object(obj):
        """
      Check if the argument is a groupable object.
      Check the constant 'Utils.IS_GROUPABLE' for a list of groupable objects.

      Parameters
      ----------
      obj: object
          Object to be verified.
      
      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """
        return Utils.get_uaibot_type(obj) in Utils.IS_GROUPABLE

    @staticmethod
    def is_a_obj_sim(obj):
        """
      Check if the argument is an object that can be put into the simulator.
      Check the constant 'Utils.IS_OBJ_SIM' for a list of objects that can be put in the simulator.
      
      Parameters
      ----------
      obj: object
          Object to be verified.
      
      Returns
      -------
      is_type: boolean
          If the object is of the type.   
      """
        return Utils.get_uaibot_type(obj) in Utils.IS_OBJ_SIM

    @staticmethod
    def is_url_available(url, types):
        """
      Try to access the content of the url 'url'. Also verifies if the content is one of the extensions contained in
      'types' (e.g, types = ['png', 'bmp', 'jpg', 'jpeg'] for images).

      Never throws an Exception, always returning a string with a message. Returns 'ok!' if and only if the
      url was succesfully acessed and has the correct file type.

      Parameters
      ----------
      url: string
          The url string.

      types: list of string
          The desired content extensions.

      Returns
      -------
      message: string
          Message.
      """

        if not (str(type(url)) == "<class 'str'>"):
            return " is not a valid url"

        ind = url.rfind('.')
        filetype = url[ind + 1:]

        if not (filetype in types):
            return " must be an file of the types: '" + str(types) + "'"

        try:
            h = httplib2.Http()
            resp = h.request(url, 'HEAD')
            if int(resp[0]['status']) < 400:
                return "ok!"
            else:
                return " : not able to access '" + url + "'."
        except:
            return " : not able to access '" + url + "'."

    #######################################
    # Plotting functions
    #######################################

    @staticmethod
    def plot(xv, yv, title="", xname="x", yname="y", labels=""):

        fig = px.line(width=800, height=400)

        # Error handling

        if not Utils.is_a_matrix(yv):
            raise Exception("The parameter 'yv' should be a matrix.")

        n = 1 if len(np.shape(yv)) == 1 else np.shape(yv)[0]
        m = np.shape(yv)[0] if len(np.shape(yv)) == 1 else np.shape(yv)[1]


        if xv is None:
            xv = list(np.arange(0, m))

        if Utils.is_a_number(xv):
            xv = list(np.arange(0, xv * m, xv))


        if not Utils.is_a_vector(xv):
            raise Exception("The parameter 'xv' should be a vector")

        if not Utils.is_a_matrix(yv, None, m):
            raise Exception("The parameter 'yv' should be a matrix with " + str(m) + " columns.")



        list_names = []

        if str(type(labels)) == "<class 'str'>":
            for i in range(n):
                list_names.append(labels + "_" + str(i + 1))
        else:
            if str(type(labels)) == "<class 'list'>" and len(labels) == n:
                for i in range(n):
                    if str(type(labels[i])) == "<class 'str'>":
                        list_names.append(labels[i])
                    else:
                        raise Exception(
                            "Optional parameter 'labels' must be either a string or a list of " + str(n) + " strings")
            else:
                raise Exception(
                    "Optional parameter 'labels' must be either a string or a list of " + str(n) + " strings")

        # end error handling
        if n > 1:
            for i in range(n):
                fig.add_scatter(x=xv, y=yv[i,:].tolist()[0], mode="lines", name=list_names[i])
        else:
            fig.add_scatter(x=xv, y=yv.tolist()[0], mode="lines", name=list_names[0])

        fig.update_xaxes(title_text=xname)
        fig.update_yaxes(title_text=yname)
        fig.show()

        return fig

    #######################################
    # Distance computation functions
    #######################################

    @staticmethod
    def fun_Int(v, h, L):

        def fun_J(u):
            return Utils._CONSTJA / ((Utils._CONSTJA - 1) * sqrt(Utils._PI * u * u) + sqrt(
                Utils._PI * u * u + Utils._CONSTJA * Utils._CONSTJA))

        v = abs(v)
        if v <= L:
            a1 = exp(-(L - v) ** 2 / (2 * h * h)) * fun_J((v - L) / (Utils._SQRT2 * h))
            a2 = exp(-(L + v) ** 2 / (2 * h * h)) * fun_J((v + L) / (Utils._SQRT2 * h))
            return -h * h * log(Utils._SQRTHALFPI * (h / (2 * L)) * (2 - a1 - a2))
        else:
            a1 = fun_J((v - L) / (Utils._SQRT2 * h))
            a2 = exp(-2 * L * v / (h * h)) * fun_J((v + L) / (Utils._SQRT2 * h))
            return 0.5 * (v - L) ** 2 - h * h * log(Utils._SQRTHALFPI * (h / (2 * L)) * (a1 - a2))

    @staticmethod
    def fun_Cir(v, h, r):

        def fun_I0hat(u):
            return pow(1 + 0.25 * u * u, -0.25) * (1 + Utils._CONSTI0HAT1 * u * u) / (1 + Utils._CONSTI0HAT2 * u * u)

        def fun_f(nu, rho):
            a1 = exp(-0.5 * (rho - nu) ** 2)
            a2 = exp(-0.5 * (rho + nu) ** 2)
            return rho * (a1 + a2) * fun_I0hat(rho * nu)

        def fun_fhat(nu, rho, arg_rhobar):
            a1 = exp(-0.5 * (rho - nu) ** 2 + 0.5 * (arg_rhobar - nu) ** 2)
            a2 = exp(-0.5 * (rho + nu) ** 2 + 0.5 * (arg_rhobar - nu) ** 2)
            return rho * (a1 + a2) * fun_I0hat(rho * nu)

        v = abs(v)
        N = 7
        node = [0.94910, -0.74153, -0.40584, 0, 0.40584, 0.74153, 0.94910]
        weight = [0.12948, 0.27970, 0.38183, 0.4179, 0.38183, 0.27970, 0.12948]

        if v <= r:
            f_low = max(0, sqrt((v / h) ** 2 + 1) - 3)
            f_up = min(r / h, sqrt((v / h) ** 2 + 1) + 3)
            delta = 0.5 * (f_up - f_low)
            y = 0
            for i in range(N):
                y = y + weight[i] * fun_f(v / h, f_low + delta * (node[i] + 1))

            y = delta * y
            return -h * h * log(y * (h / r) * (h / r))
        else:
            f_low = 0
            f_up = r / h
            delta = 0.5 * (f_up - f_low)
            rhobar = f_low + delta * (node[N - 1] + 1)
            y = 0
            for i in range(N):
                y = y + weight[i] * fun_fhat(v / h, f_low + delta * (node[i] + 1), rhobar)

            y = delta * y
            return 0.5 * (v - h * rhobar) ** 2 - h * h * log(y * (h / r) * (h / r))

    @staticmethod
    def fun_Sph(v, h, r):

        v = abs(v)
        c = 3 * (h ** 2) / (2 * r ** 3)

        if v <= r:
            if v == 0:
                return -h * h * log(
                    c * (-2 * r * exp(-(r * r) / (2 * h * h)) + 2 * r * exp(-Utils.fun_Int(0, h, r) / (h * h))))
            else:
                a1 = exp(-((r + v) * (r + v) / (2 * h * h)))
                a2 = exp(-((r - v) * (r - v) / (2 * h * h)))
                return -h * h * log(c * (h * h * (a1 - a2) / v + 2 * r * exp(-Utils.fun_Int(v, h, r) / (h * h))))

        else:
            a1 = exp(-(2 * r * v / (h * h)))
            a2 = 1
            return 0.5 * (v - r) * (v - r) - h * h * log(
                c * (h * h * (a1 - a2) / v + 2 * r * exp((0.5 * (v - r) * (v - r) - Utils.fun_Int(v, h, r)) / (h * h))))

    @staticmethod
    def compute_dist(obj_a, obj_b, h=0.000001, g=0.000001, p_a_init=None, tol=0.001, no_iter_max=20):

        # Error handling

        if not Utils.is_a_simple_object(obj_a):
            raise Exception("The parameter 'obj_a' must be one of the following: " + str(Utils.IS_SIMPLE) + ".")

        if not Utils.is_a_simple_object(obj_b):
            raise Exception("The parameter 'obj_b' must be one of the following: " + str(Utils.IS_SIMPLE) + ".")

        if not Utils.is_a_number(h) or h <= 0:
            raise Exception("The optional parameter 'h' must be a nonnegative number.")

        if not Utils.is_a_number(g) or g <= 0:
            raise Exception("The optional parameter 'g' must be a nonnegative number.")

        if not (p_a_init is None or Utils.is_a_vector(p_a_init, 3)):
            raise Exception("The optional parameter 'p_a_init' must be a 3D vector or 'None'.")

        if not Utils.is_a_number(tol) or tol <= 0:
            raise Exception("The optional parameter 'tol' must be a nonnegative number.")

        if not Utils.is_a_natural_number(no_iter_max):
            raise Exception("The optional parameter 'no_iter_max' must be a nonnegative integer.")

        # end error handling

        if p_a_init is None:
            p_a = np.random.uniform(-3, 3, size=(3,))
        else:
            p_a = np.array(p_a_init)

        converged = False
        i = 0

        while (not converged) and i < no_iter_max:
            p_a_ant = p_a
            p_b, dp_a = obj_b.h_projection(p_a, g)
            p_a, dp_b = obj_a.h_projection(p_b, h)
            converged = np.linalg.norm(p_a - p_a_ant) < tol
            i += 1

        dist = np.linalg.norm(p_a - p_b)
        hg_dist = sqrt(max(2 * (dp_a + dp_b - 0.5 * dist * dist), 0))

        return p_a, p_b, hg_dist
