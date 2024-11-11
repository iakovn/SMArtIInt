within SMArtInt.Internal.InterfaceFunctions;
function initializeStates
  input SMArtIntClass smartint;
  input Real time_value;
  input Real[:] flatStateValues;
  external"C" NeuralNet_initializeStates(smartint, time_value, flatStateValues, size(flatStateValues, 1)) annotation (
    Library={"SMArtInt"},
    LibraryDirectory="modelica://SMArtInt/Resources/Library");
end initializeStates;
