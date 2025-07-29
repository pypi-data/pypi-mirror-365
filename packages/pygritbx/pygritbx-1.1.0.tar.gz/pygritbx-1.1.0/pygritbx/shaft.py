'''
This is the "Shaft" class. It inherits from "Component" class.
This class is responsible for defining the properties of a Shaft object, such as:

I) Given properties:
--> 1) "inputs": a list containing component objects representing the inputs from the shaft's perspective
--> 2) "outputs": a list containing component objects representing the outputs from the shafts's perspective
--> 3) "sups": a list containing support objects representing the bearings on the shaft
--> 4) "material": a Material object representing the material properties of the shaft
--> 5) "sections": a list of shaft section objects representing the sections at which to perform static/fatigue analysis
--> 6) "profiles": a list of shaft profile objects representing the profile of the shaft (could be more than one for different type of analyses)

II) Calculated properties:
--> 1) "N": an n-element vector representing the normal internal load distribution along the shaft's axis
--> 2) "Mx": an n-element vector representing the bending moment around x-axis  internal load distribution along the shaft's axis
--> 3) "My": an n-element vector representing the bending moment around y-axis  internal load distribution along the shaft's axis
--> 4) "Mt": an n-element vector representing the torsional moment around z-axis internal load distribution along the shaft's axis

Moreover, the user can carry out all the necessary calculations via the following functions:
--> 1) "solve(self)": implementation of virtual function from parent class resolving the external force(s)/torque(s) acting on the shaft.
--> 2) "checkTorqueEquilibrium(self)": implmenetation of virtual function from parent class to check torque equilibrium on shaft by involving external torques and forces, the latter with their corresponding locations with respect to the shaft.
--> 3) "calculateTorque(self, comp=None)": calculates the external torque acting on the shaft due to component "comp" with unknown torque. Adds the torque to the shaft's "ETs" and the component's "ETs".
--> 4) "addProfile(self, profile=None)": adds profile to the list of profiles "self.profiles" if it doesn't exist yet in the list.
--> 5) "addSection(self, sections=[])": adds the list of sections to "self.sections".
--> 6) "insertFLCF(self)": inserts fatigue limit correction factors to the sections in "self.sections".
--> 7) "calculateReactionForces(self)": calculates the forces on the bearings of the shaft by imposing equilibrium conditions with all external forces in "self.EFs".
--> 8) "performStaticVerification(self, RF=None, profile=None)": performs static verification on all sections in "self.sections" relative to the shaft's given profile.
--> 9) "performFatigueVerification(self, RF=None, profile=None)": perform fatigue verification on all sections in "self.sections" relative to the shaft's given profile.
--> 10) "calculateInternalLoads(self, RF=None, profile=None)": calculates the internal loads acting on the shaft relative to the given profile.
--> 11) "calculateStresses(self, profile=None)": calculates the stresses acting on the shaft relative the shaft's given profile.
--> 12) "calculateEquivalentAndIdealStress(self, profile=None)": calculates equivalent and ideal stresses along the shaft's given profile.
--> 13) "plotInternalLoads(self, profile=None)": plots the internal loads acting on the shaft relative to the shaft's given profile.
--> 14) "plotLoad(self, load=[], ylabel="", title="", profile=None)": generic function to plot an internal load/stress acting on the shaft relative to the shaft's given profile.
--> 15) "calculateStaticSafetyFactor(self, profile=None)": calculates the static safety factor on all sections in "self.sections" relative to the shaft's given profile.
--> 16) "calculateMeanAlternatingStress(self, profile=None)": calculates the mean and alternating stresses on all sections in "self.sections" relative the shaft's given profile.
--> 17) "calculateEquivalentStresses(self)": calculates the equivalent mean and alternating stresses on all sections in "self.sections".
--> 18) "calculateFatigueSafetyFactor(self)": calculates the fatigue safety factor on all sections in "self.sections".
'''

import numpy as np
import matplotlib.pyplot as plt
from .component import Component
from .torque import Torque
from .force import Force
from .gear import Gear
from .motor import Motor
from math import pi
class Shaft(Component):

    # Constructor
    def __init__(self, name="", inputs=[], outputs=[], axis=np.zeros(3), material=None, sups=[], loc=0):
        # Given parameters
        super().__init__(name=name, material=material, axis=axis, loc=loc, omega=inputs[0].omega)
        # Update shaft's absolute location
        if self.abs_loc.size == 0:
            self.abs_loc = -inputs[0].rel_loc + inputs[0].abs_loc
        # Inputs
        for input in inputs:
            input.onShaft = self
            input.updateLoc()
            if isinstance(input, Motor):
                input.updateForceLoc()
                input.updateTorqueLoc()
            if input.ETs.size != 0:
                self.updateETs(input.ETs)
        self.inputs = inputs
        # Outputs
        for out in outputs:
            out.onShaft = self
            out.updateLoc()
            if out.ETs.size != 0:
                self.updateETs(out.ETs)
            out.omega = self.omega
        self.outputs = outputs
        
        # Supports
        for sup in sups:
            sup.onShaft = self
            sup.updateLoc()
            sup.omega = self.omega
            sup.n = sup.omega * 30 / pi
        self.supports = sups
        # Sections
        self.sections = np.array([])
        # Profiles
        self.profiles = np.array([])
        # Internal Loads
        self.N = np.array([])
        self.Mx = np.array([])
        self.My = np.array([])
        self.Mt = np.array([])
    
    # Solve function
    def solve(self):
        unknown_Ts = 0
        unknkown_Fs = 0
        unknown_comp_T = None
        comps = np.append(self.inputs, self.outputs)
        if not self.checkTorqueEquilibrium():
            print(f"Checking solvability for {self.name}.")
            for comp in comps:
                if comp.ETs.size == 0:
                    unknown_Ts += 1
                    unknown_comp_T = comp
                else:
                    self.updateETs(comp.ETs)
                if comp.EFs.size == 0 and not isinstance(comp, Motor):
                    unknkown_Fs += 1
                else:
                    self.updateEFs(comp.EFs)
            if unknown_Ts > 1:
                print(f"{self.name}'s torque equilibrium cannot be solved.")
            elif unknown_Ts == 1:
                print(f"Solving torque equilibrium for {self.name}.")
                self.calculateTorque(unknown_comp_T)
                print(f"Torque equilibrium for {self.name} is solved.")
                if isinstance(unknown_comp_T, Gear):
                    choice = input(f"Detected torque on {unknown_comp_T.name}. Would you like to solve its torque equilibrium [y/n]: ")
                    if choice == 'y' or choice == 'Y':
                        unknown_comp_T.solve()
                        unknkown_Fs -= 1
                    else:
                        print(f"{unknown_comp_T.name}'s torque equilibrium won't be solved now.")
        else:
            print(f"No torque equilibrium to be solved for {self.name}.")
        if unknkown_Fs == 0:
            if self.checkForceEquilibrium() :
                print(f"No force equilibrium to be solved for {self.name}.")
            else:
                reaction_choice = input(f"Forces from external components on {self.name} are resolved. Do you want to calculate the reaction forces [y/n]: ")
                if reaction_choice == 'y' or reaction_choice == 'Y':
                    self.calculateReactionForces()
                    self.checkForceEquilibrium()
                else:
                    print(f"Reaction forces on {self.name} won't be calculated.")
        else:
            print(f"Force equilibrium for {self.name} cannot be solved.")
            
        
    # Check torque equilibrium
    def checkTorqueEquilibrium(self):
        print(f"Checking torque equilibrium for {self.name}.")
        valid = True
        if self.ETs.size == 0:
            valid = False
            return valid
        eq = np.zeros(3)
        eqState = False
        for ET in self.ETs:
            eq = eq + ET.torque
        if all(np.abs(eq) <= 1e-3 * np.ones(3)):
            print(f"{self.name} mainatains a torque equilibrium.")
            eqState = True
        else:
            print(f"{self.name} does not mainatain a torque equilibrium.")
        return eqState
    
    # Calculate torque
    def calculateTorque(self, comp=None):
        ET = Torque(-np.sum(self.ETs), comp.abs_loc)        
        comp.updateETs([ET])
        self.updateETs([ET])
    
    # Set shaft profile
    def addProfile(self, profile=None):
        if profile not in self.profiles:
            profile.shaft = self
            profile.calculateSectionProperties()
            self.profiles = np.append(self.profiles, profile)
    
    # Add sections
    def addSections(self, sections=[]):
        for section in sections:
            section.material = self.material
        self.sections = np.append(self.sections, sections)
    
    # Insert fatigue limit corrector factors
    def insertFLCF(self):
        for section in self.sections:
            section.addFLCF()
    
    # Calculate reaction forces
    def calculateReactionForces(self):
        # Gears axial load
        K_a = np.zeros(3)
        for EF in self.EFs:
            K_a = K_a + (EF.force * self.axis)
        K_a = np.sum(K_a)
        # Find the bearing around which to apply moment
        index = 0
        for i in range(len(self.supports)):
            if self.supports[i].type == "Pin":
                index = i
                self.supports[index].F_tot = Force(np.zeros(3), self.supports[index].abs_loc)
        # Calculate reaction on other bearing
        bearingSupportsAxial = False
        for i in range(len(self.supports)):
            if i != index:
                if self.supports[i].bearingType == "Tapered" or self.supports[i].bearingType == "Contact Ball":
                    bearingSupportsAxial = True
                self.supports[i].F_tot = Force(np.zeros(3), self.supports[i].abs_loc)
                supDist = self.supports[i].abs_loc - self.supports[index].abs_loc
                supDist_rec = np.array([1/d if d != 0 else 0 for d in supDist])
                for EF in self.EFs:
                    momEF = EF.moment(location=self.supports[index].abs_loc) #np.cross(EF.force, (EF.loc - self.supports[index].abs_loc)) * 1e-3
                    self.supports[i].F_tot.force += np.cross(momEF, supDist_rec) * 1e3
                self.supports[index].F_tot.force -= self.supports[i].F_tot.force
        # Calculate reaction around bearing with sum of external forces
        for EF in self.EFs:
            if bearingSupportsAxial:
                self.supports[index].F_tot.force -= EF.force*(1 - self.axis)
            else:
                self.supports[index].F_tot.force -= EF.force
        # Update axial load based on configuration
        if (self.supports[0].bearingType == "Tapered" and self.supports[1].bearingType == "Tapered") or (self.supports[0].bearingType == "Contact Ball" and self.supports[1].bearingType == "Contact Ball"):
            if self.supports[0].shoulder == -1:
                indA = 1
                indB = 0
            else:
                indA = 0
                indB = 1
            btype = self.supports[indA].bearingType
            A_FrV = self.supports[indA].F_tot.force - (self.supports[indA].F_tot.force * self.axis)
            A_Fr = np.sqrt(np.sum(A_FrV * A_FrV))
            A_Y = self.supports[indA].Y
            B_FrV = self.supports[indB].F_tot.force - (self.supports[indB].F_tot.force * self.axis)
            B_Fr = np.sqrt(np.sum(B_FrV * B_FrV))
            B_Y = self.supports[indB].Y
            print(f"Axial reaction forces on {self.name} with {btype} bearings: ", end="")
            # Tapered
            if btype == "Tapered":
                # Case 1
                if K_a > 0:
                    # Factor of comparison
                    fac = (B_Fr / B_Y) - (A_Fr / A_Y)
                    # Case 1a
                    if fac <= 0:
                        print("Case 1a")
                        A_Fa = 0.5 * A_Fr / A_Y
                        B_Fa = -(K_a + A_Fa)
                    # Case 1b
                    elif fac > 0 and K_a >= 0.5 * fac:
                        print("Case 1b")
                        A_Fa = 0.5 * A_Fr / A_Y
                        B_Fa = -(K_a + A_Fa)
                    # Case 1c
                    elif fac > 0 and K_a < 0.5 * fac:
                        print("Case 1c")
                        B_Fa = -0.5 * B_Fr / B_Y
                        A_Fa = -(K_a + B_Fa)
                # Case 2
                else:
                    # Factor of comparison
                    fac = A_Fr / A_Y - B_Fr / B_Y
                    # Case 2a
                    if fac <= 0 and np.abs(K_a) >= 0:
                        print("Case 2a")
                        B_Fa =  -0.5 * B_Fr / B_Y
                        A_Fa = -(B_Fa + K_a)
                    # Case 2b
                    elif fac > 0 and np.abs(K_a) >= 0.5 * fac:
                        print("Case 2b")
                        B_Fa = -0.5 * B_Fr / B_Y
                        A_Fa = -(B_Fa + K_a)
                    # Case 2c
                    elif fac > 0 and np.abs(K_a) < 0.5 * fac:
                        print("Case 2c")
                        A_Fa = 0.5 * A_Fr / A_Y
                        B_Fa = -(A_Fa + K_a)
            # Contact Ball
            else:
                # Case 1
                if K_a > 0:
                    # Case 1a
                    if A_Fr >= B_Fr:
                        print("Case 1a")
                        A_Fa = self.supports[indA].R * A_Fr
                        B_Fa = -(A_Fa + K_a)
                    # Case 1b
                    elif (A_Fr < B_Fr) and (K_a >= self.supports[indA].R * (B_Fr - A_Fr)):
                        print("Case 1b")
                        A_Fa = self.supports[indA].R * A_Fr
                        B_Fa = -(A_Fa + K_a)
                    # Case 1c
                    elif (A_Fr < B_Fr) and (K_a < self.supports[indA].R * (B_Fr - A_Fr)):
                        print("Case 1c")
                        B_Fa = -self.supports[indB].R * B_Fr
                        A_Fa = -(B_Fa + K_a)
                # Case 2
                else:
                    # Case 2a
                    if A_Fr <= B_Fr:
                        print("Case 2a")
                        B_Fa = -self.supports[indB].R * B_Fr
                        A_Fa = -(B_Fa + K_a)
                    # Case 2b
                    elif (A_Fr > B_Fr) and (np.abs(K_a) >= self.supports[indA].R * (A_Fr - B_Fr)):
                        print("Case 2b")
                        B_Fa = -self.supports[indB].R * B_Fr
                        A_Fa = -(B_Fa + K_a)
                    # Case 2c
                    elif (A_Fr > B_Fr) and (np.abs(K_a) < self.supports[indA].R * (A_Fr - B_Fr)):
                        print("Case 2c")
                        A_Fa = self.supports[indA].R * A_Fr
                        B_Fa = -(A_Fa + K_a)
            
            self.supports[indA].F_tot.force += (A_Fa * self.axis)
            self.supports[indB].F_tot.force += (B_Fa * self.axis)
        # Update the external forces on the shaft
        for support in self.supports:
            self.updateEFs([support.F_tot])
        # Update support reaction to separate total radial force and axial force
        for support in self.supports:
            support.updateReaction()
    
    # Perform static verification
    def performStaticVerification(self, RF=None, profile=None):
        if profile == None:
            profile = self.profiles[0]
        print(f"Initiating static verification on shaft {self.name}.")
        self.calculateInternalLoads(RF=RF, profile=profile)
        plotInteralLoadsChoice = input(f"Would you like to plot shaft {self.name}'s internal loads? [y/n]: ")
        if plotInteralLoadsChoice == "Y" or plotInteralLoadsChoice == "y":
            self.plotInternalLoads(profile=profile)
        print(f"Calculating stresses on shaft {self.name} along profile '{profile.name}'.")
        self.calculateStresses(profile=profile)
        self.calculateEquivalentAndIdealStress(profile=profile)
        plotStressesChoice = input(f"Woud you like to plot profile '{profile.name}''s stresses? [y/n]: ")
        if plotStressesChoice == "Y" or plotStressesChoice == "y":
            profile.plotStresses()
        print(f"Calculating static safety factor for every user-defined section.")
        self.calculateStaticSafetyFactor(profile=profile)
        print(f"Section Name: Static Safety Factor")
        for section in self.sections:
            print(f"Section {section.name}: {section.staticSF:.2f} [-].")
    
    # Perform fatigue verification
    def performFatigueVerification(self, RF=None, profile=None):
        if profile == None:
            profile = self.profiles[0]
        print(f"Initiating fatigue verification on shaft {self.name}.")
        self.calculateInternalLoads(RF=RF, profile=profile)
        plotInteralLoadsChoice = input(f"Would you like to plot shaft {self.name}'s internal loads? [y/n]: ")
        if plotInteralLoadsChoice == "Y" or plotInteralLoadsChoice == "y":
            self.plotInternalLoads(profile=profile)
        print(f"Calculating stresses on shaft {self.name} along profile '{profile.name}'.")
        self.calculateStresses(profile=profile)
        self.calculateEquivalentAndIdealStress(profile=profile)
        plotStressesChoice = input(f"Woud you like to plot profile '{profile.name}''s stresses? [y/n]: ")
        if plotStressesChoice == "Y" or plotStressesChoice == "y":
            profile.plotStresses()
        print(f"Calculating mean and alternating stresses for every user-defined section.")
        self.calculateMeanAlternatingStress(profile=profile)
        print(f"Calculating fatigue limit corrector factors on every user-defined section.")
        self.insertFLCF()
        print(f"Calculating equivalent mean and alternating stresses along every user-defined section.")
        self.calculateEquivalentStresses()
        plotHaighDiagramChoice = input("Would you like to plot the Haigh Diagram for every defined section? [y/n]:")
        if plotHaighDiagramChoice == "Y" or plotHaighDiagramChoice == "y":
            for section in self.sections:
                section.plotHaighDiagram()
        print(f"Calculating fatigue safety factor for every user-defined section.")
        self.calculateFatigueSafetyFactor()
        print("Section Name: Fatigue Safety Factor")
        for section in self.sections:
            print(f"{section.name}: {section.fatigueSF:.2f} [-].")
        
    
    # Calculate internal loads
    def calculateInternalLoads(self, RF=None, profile=None):
        if profile == None:
            profile = self.profiles[0]
        if self.N.size != 0 and self.Mx.size != 0 and self.My.size != 0 and self.Mt.size != 0:
            print(f"Internal loads for shaft {self.name} already calculated.")
            return
        print(f"Calculating internal loads on shaft {self.name}.")
        l = len(self.profiles[0].locs)
        self.N = np.zeros(l)
        self.Mx = np.zeros(l)
        self.My = np.zeros(l)
        self.Mt = np.zeros(l)
        for EF in self.EFs:
            for i, z in enumerate(profile.locs):
                if np.dot(EF.loc - self.abs_loc, np.abs(self.axis)) <= z:
                    self.N[i] = self.N[i] - np.sum(EF.force * np.abs(self.axis))
                    mxz = EF.moment(axis=RF[1], projection=RF[2])
                    mxy = EF.moment(location=z - EF.loc, axis=RF[2], projection=RF[1])
                    self.Mx[i] = self.Mx[i] + (mxz - mxy)
                    myz = EF.moment(axis=RF[0], projection=RF[2])
                    myx = EF.moment(location=EF.loc - z, axis=RF[2], projection=RF[0])
                    self.My[i] = self.My[i] + (myz + myx)
        for ET in self.ETs:
                for i, z in enumerate(profile.locs):
                    if np.dot(ET.loc - self.abs_loc, np.abs(self.axis)) <= z:
                        self.Mt[i] = self.Mt[i] + np.sum(ET.torque)
        self.N[np.where(np.abs(self.N) < 1e-3)] = 0
        self.Mx[np.where(np.abs(self.Mx) < 1e-3)] = 0
        self.My[np.where(np.abs(self.My) < 1e-3)] = 0
        self.Mt[np.where(np.abs(self.Mt) < 1e-3)] = 0
        self.Mf = np.sqrt(self.Mx ** 2 + self.My ** 2)
    
    # Calculate stresses
    def calculateStresses(self, profile=None):
        if profile == None:
            profile = self.profiles[0]
        profile.calculateProfileStresses()
    
    # Calculate equivalent and ideal stresses
    def calculateEquivalentAndIdealStress(self, profile=None):
        if profile == None:
            profile = self.profiles[0]
        profile.calculateProfileEquivalentAndIdealStress()
    
    # Plot internal loads
    def plotInternalLoads(self, profile=None):
        if profile == None:
            profile = self.profiles[0]
        # Normal load
        self.plotLoad(load=self.N, ylabel="N [N]", title="Normal Load - N(z)", profile=profile)
        # Bending moment around x-axis
        self.plotLoad(load=self.Mx, ylabel=r"$M_{x}$ [Nm]", title=r"Bending Moment $M_{x}(z)$", profile=profile)
        # Bending moment around y-axis
        self.plotLoad(load=self.My, ylabel=r"$M_{y}$ [Nm]", title=r"Bending Moment $M_{y}(z)$", profile=profile)
        # Resulting bending moment
        self.plotLoad(load=self.Mf, ylabel=r"$M_{B}$ [Nm]", title=r"Bending Moment $M_{B}(z)$", profile=profile)
        # Torsional moment
        self.plotLoad(load=self.Mt, ylabel=r"$M_{t}$ [Nm]", title=r"Torsional Moment $M_{t}(z)$", profile=profile)
    
    # Plot load with shaft profile
    def plotLoad(self, load=[], ylabel="", title="", profile=None):
        if profile == None:
            profile = self.profiles[0]
        fig, ax = plt.subplots()
        ax.plot(profile.locs, load, 'b', linewidth = 1.5)
        ax.set_xlabel("z [mm]")
        ax.set_ylabel(ylabel)
        plt.title(title)
        if np.max(np.abs(load)) != 0:
            ax.set_ylim(-1.1 * np.max(np.abs(load)), 1.1 * np.max(np.abs(load)))
        else:
            ax.set_ylim(-1, 1)
        plt.grid()
        profile.plotProfile(ax)
        for section in self.sections:
            xs = np.ones(2) * np.sum(section.loc)
            ys = np.array([-1, 1])
            if np.max(np.abs(load)) != 0:
                ys = ys * 1.1 * np.max(np.abs(load))
            ax.plot(xs, ys, 'g--', linewidth=1.5)
            ax.text(xs[0] - 10, 0.9 * ys[0], section.name)
            ax.text(xs[0] - 10, 0.9 * ys[1], section.name)
        plt.show()
    
    # Calculate static safety factor on shaft's sections
    def calculateStaticSafetyFactor(self, profile=None):
        if profile == None:
            profile = self.profiles[0]
        for section in self.sections:
            section.calculateSectionStaticSafetyFactor(profile=profile)

    # Calculate mean and alternating stresses
    def calculateMeanAlternatingStress(self, profile=None):
        if profile == None:
            profile = self.profiles[0]
        for section in self.sections:
            section.calculateSectionMeanAlternatingStress(profile=profile)
    
    # Calculate equivalent mean and alternating stress
    def calculateEquivalentStresses(self):
        for section in self.sections:
            section.calculateSectionEquivalentStress()
    
    # Calculate fatigue safety factor on shaft's sections
    def calculateFatigueSafetyFactor(self):
        for section in self.sections:
            section.calculateSectionFatigueSafetyFactor()